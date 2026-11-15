"""End-to-end real HTTP tests against an isolated EchoEats SQLite database.
Run: python tests/full_workflow.py
"""
import base64
import concurrent.futures
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parent.parent

def status(resp,expect=200):
    assert resp.status_code==expect,(resp.status_code,resp.text[:350])
    return resp.json()

def launch():
    temp=tempfile.TemporaryDirectory(prefix='ee-tests-')
    with socket.socket() as s:
        s.bind(('127.0.0.1',0)); port=s.getsockname()[1]
    env=os.environ.copy(); env['ECHOEATS_DB_PATH']=str(Path(temp.name)/'test.sqlite3')
    server=subprocess.Popen([sys.executable,'-m','uvicorn','backend.main:app','--host','127.0.0.1','--port',str(port)],cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    base=f'http://127.0.0.1:{port}'
    for _ in range(50):
        try:
            if requests.get(base+'/api/health',timeout=.2).status_code==200:return temp,server,base
        except requests.RequestException:pass
        time.sleep(.1)
    err=server.stderr.read().decode() if server.poll() is not None else 'Server did not start'
    raise AssertionError(err)


def run():
    temp,server,base=launch()
    count=0
    try:
        vendor,consumer,consumer2,outsider=(requests.Session() for _ in range(4))
        for s,email in [(vendor,'vendor@echoeats.test'),(consumer,'consumer@echoeats.test')]:
            status(s.post(base+'/api/auth/login',json={'email':email,'password':'Demo12345!'}))
        count+=1; print('PASS 1. Role-specific login and independent sessions')
        assert status(vendor.get(base+'/api/session'))['role']=='vendor'
        assert status(consumer.get(base+'/api/session'))['role']=='consumer'
        # Signup with own credentials
        status(consumer2.post(base+'/api/auth/signup',json={'name':'Test customer','email':'testcustomer@example.test','password':'Strong1234','role':'consumer'}))
        assert status(consumer2.get(base+'/api/session'))['role']=='consumer'
        count+=1;print('PASS 2. Consumer registration persists and signs in')
        start=time.time()
        from datetime import datetime,timedelta,timezone
        pickup=(datetime.now(timezone.utc)+timedelta(hours=3)).isoformat()
        expiration=(datetime.now(timezone.utc)+timedelta(hours=4)).isoformat()
        good=dict(name='Full App Test Lunch',description='Freshly prepared lunch',category='Meals',emoji='🥗',dietary='Vegetarian',quantity=1,original_price=5.5,initial_price=3.5,min_price=1.5,pickup_deadline=pickup,expires_at=expiration,pricing_curve='exponential')
        foodid=status(vendor.post(base+'/api/listings',json=good))['id']
        food=next(f for f in status(vendor.get(base+'/api/snapshot'))['listings'] if f['id']==foodid)
        assert food['pricing_curve']=='exponential' and food['quantity']==1
        count+=1;print('PASS 3. Vendor created food with chosen dynamic pricing curve')
        # Atomic reserve race; only one can get the last item
        def try_reserve(s):
            resp=s.post(base+'/api/reservations',json={'listing_id':foodid,'quantity':1},timeout=6)
            return resp.status_code,resp.json()
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            a,b=list(pool.map(try_reserve,[consumer,consumer2]))
        assert sorted([a[0],b[0]])==[200,409],(a,b)
        winner=consumer if a[0]==200 else consumer2
        rid=(a[1] if a[0]==200 else b[1])['id']
        food=next(f for f in status(vendor.get(base+'/api/snapshot'))['listings'] if f['id']==foodid)
        assert food['quantity']==0
        count+=1;print('PASS 4. Concurrent users cannot claim the same last portion')
        reserved=next(r for r in status(winner.get(base+'/api/snapshot'))['reservations'] if r['id']==rid)
        assert reserved['status']=='pending' and reserved['locked_unit_price']>0
        assert 13.5*60 < (datetime.fromisoformat(reserved['expires_at'])-datetime.fromisoformat(reserved['created_at'])).total_seconds()<16.5*60
        count+=1;print('PASS 5. 15-minute hold and locked price')
        denied=consumer2 if winner is consumer else consumer
        status(denied.post(base+f'/api/reservations/{rid}/pay'),404)
        paid=status(winner.post(base+f'/api/reservations/{rid}/pay'))
        assert paid['status']=='confirmed' and paid['pickup_code'].startswith('EE-')
        status(winner.post(base+f'/api/reservations/{rid}/pay'),409)
        count+=1;print('PASS 6. Demo payment, ownership checks, duplicate-payment rejection')
        status(vendor.post(base+f'/api/reservations/{rid}/collect'))
        assert next(r for r in status(vendor.get(base+'/api/snapshot'))['reservations'] if r['id']==rid)['status']=='collected'
        status(vendor.post(base+f'/api/reservations/{rid}/collect'),409)
        count+=1;print('PASS 7. Pickup confirmation and invalid status transitions blocked')
        # Create another food listing and expire hold by moving expiry into past.
        good['name']='Test Expiry';good['quantity']=2
        second=status(vendor.post(base+'/api/listings',json=good))['id']
        another=status(consumer.post(base+'/api/reservations',json={'listing_id':second,'quantity':1}))
        assert another['status']=='pending'
        with sqlite3.connect(Path(temp.name)/'test.sqlite3') as db:
            db.execute("UPDATE reservations SET expires_at='2000-01-01T00:00:00+00:00' WHERE id=?",(another['id'],))
            db.commit()
        assert next(r for r in status(consumer.get(base+'/api/snapshot'))['reservations'] if r['id']==another['id'])['status']=='expired'
        secondfood=next(f for f in status(vendor.get(base+'/api/snapshot'))['listings'] if f['id']==second)
        assert secondfood['quantity']==2
        count+=1;print('PASS 8. Expiration releases inventory automatically')
        # Cancel another unpaid hold
        tempres=status(consumer.post(base+'/api/reservations',json={'listing_id':second,'quantity':1}))
        status(consumer.post(base+f"/api/reservations/{tempres['id']}/cancel"))
        assert next(f for f in status(vendor.get(base+'/api/snapshot'))['listings'] if f['id']==second)['quantity']==2
        count+=1;print('PASS 9. Consumer cancellation releases inventory')
        # Validation, role authorization, delete/deactivate
        status(consumer.post(base+'/api/listings',json=good),403)
        status(consumer2.delete(base+'/api/listings/'+second),403)
        status(vendor.delete(base+'/api/listings/'+second))
        status(consumer.post(base+'/api/reservations',json={'listing_id':second,'quantity':1}),409)
        count+=1;print('PASS 10. Role checks and deactivated listings')
        # Update profile + password
        status(consumer.patch(base+'/api/profile',json={'name':'Edited consumer','phone':'+97330000000'}))
        assert status(consumer.get(base+'/api/session'))['name']=='Edited consumer'
        status(consumer.post(base+'/api/auth/change-password',json={'current_password':'Demo12345!','new_password':'Changed1234!'}))
        status(consumer.post(base+'/api/auth/logout'))
        status(consumer.post(base+'/api/auth/login',json={'email':'consumer@echoeats.test','password':'Changed1234!'}))
        count+=1;print('PASS 11. Profile changes and password updates')
        # Food photo
        png=(b'\x89PNG\r\n\x1a\n'+b'valid-demo-header')
        photo=status(vendor.post(base+'/api/photos',json={'data':'data:image/png;base64,'+base64.b64encode(png).decode()}))
        assert photo['url'].startswith('/uploads/')
        assert vendor.get(base+photo['url']).status_code==200
        count+=1;print('PASS 12. Vendor food photo upload and retrieval')
        # Restore to demo, don't ship current test's sqlite
        print(f'\nPASS {count}/{count} full application integration tests in {time.time()-start:.1f}s')
    finally:
        server.terminate()
        try:server.wait(timeout=3)
        except subprocess.TimeoutExpired:server.kill()
        temp.cleanup()

if __name__=='__main__':run()
