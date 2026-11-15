"""EchoEats – running multi-user student marketplace (FastAPI + SQLite).

Features: local accounts, vendor listings, photo uploads, pricing curves, atomic
inventory holds, 15-minute expirations, demo checkout, pickup confirmation.
No real card details, external services, or payment processing.
"""
from __future__ import annotations
import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import threading
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent.parent
DB = Path(os.getenv('ECHOEATS_DB_PATH', str(ROOT / 'echoeats.sqlite3')))
UPLOAD = ROOT / 'uploads'
UPLOAD.mkdir(parents=True, exist_ok=True)
SESSION_SECONDS = 30 * 60
RESERVATION_SECONDS = 15 * 60
DEMO_PASSWORD = 'Demo12345!'

app = FastAPI(title='EchoEats – Working Application', version='2.0.0', docs_url='/api/docs', openapi_url='/api/openapi.json')


def now():
    return datetime.now(timezone.utc)


def iso(dt=None):
    return (dt or now()).isoformat(timespec='milliseconds')


def dtime(s):
    return datetime.fromisoformat(str(s).replace('Z', '+00:00')).astimezone(timezone.utc)


def ident():
    return str(uuid.uuid4())


def hash_pw(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 220_000)
    return salt.hex() + ':' + digest.hex()


def verify_pw(password, stored):
    try:
        salt, actual = stored.split(':', 1)
        guess = hash_pw(password, bytes.fromhex(salt)).split(':')[1]
        return hmac.compare_digest(guess, actual)
    except Exception:
        return False


def fail(message, code=400):
    raise HTTPException(status_code=code, detail=message)


@contextmanager
def connection(write=False):
    db = sqlite3.connect(str(DB), timeout=20, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA busy_timeout=20000')
    try:
        if write:
            db.execute('BEGIN IMMEDIATE')
        else:
            db.execute('BEGIN')
        yield db
        db.execute('COMMIT')
    except Exception:
        try: db.execute('ROLLBACK')
        except Exception: pass
        raise
    finally:
        db.close()


def row(r):
    return dict(r) if r is not None else None


def one(db, sql, args=()):
    return row(db.execute(sql, args).fetchone())


def many(db, sql, args=()):
    return [row(r) for r in db.execute(sql, args).fetchall()]


def init_db():
    DB.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(str(DB), timeout=30)
    db.executescript('''
    PRAGMA journal_mode=WAL;
    PRAGMA foreign_keys=ON;
    CREATE TABLE IF NOT EXISTS users (
       id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
       phone TEXT DEFAULT '', password_hash TEXT NOT NULL,
       role TEXT NOT NULL CHECK(role IN ('consumer','vendor')),
       vendor_name TEXT DEFAULT '', address TEXT DEFAULT '',
       failed_attempts INTEGER DEFAULT 0, locked_until TEXT,
       created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sessions (
       token_hash TEXT PRIMARY KEY, user_id TEXT NOT NULL REFERENCES users(id),
       last_active TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS listings (
       id TEXT PRIMARY KEY, vendor_id TEXT NOT NULL REFERENCES users(id),
       name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
       category TEXT NOT NULL, dietary TEXT NOT NULL DEFAULT '',
       emoji TEXT NOT NULL DEFAULT '🥡', image_url TEXT DEFAULT '',
       quantity INTEGER NOT NULL CHECK(quantity>=0),
       initial_quantity INTEGER NOT NULL CHECK(initial_quantity>=0),
       original_price REAL NOT NULL CHECK(original_price>0),
       initial_price REAL NOT NULL CHECK(initial_price>0),
       min_price REAL NOT NULL CHECK(min_price>0),
       current_price REAL NOT NULL CHECK(current_price>0),
       demand_count INTEGER NOT NULL DEFAULT 0,
       pickup_deadline TEXT NOT NULL, expires_at TEXT NOT NULL,
       pricing_curve TEXT NOT NULL DEFAULT 'linear',
       last_price_update TEXT NOT NULL, active INTEGER NOT NULL DEFAULT 1,
       created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_listings_vendor ON listings(vendor_id);
    CREATE TABLE IF NOT EXISTS reservations (
       id TEXT PRIMARY KEY, listing_id TEXT NOT NULL REFERENCES listings(id),
       vendor_id TEXT NOT NULL REFERENCES users(id),
       consumer_id TEXT NOT NULL REFERENCES users(id),
       consumer_name TEXT NOT NULL, quantity INTEGER NOT NULL CHECK(quantity>0),
       locked_unit_price REAL NOT NULL, status TEXT NOT NULL
           CHECK(status IN ('pending','confirmed','expired','cancelled','collected')),
       created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
       paid_at TEXT, collected_at TEXT, refunded_at TEXT, pickup_code TEXT UNIQUE
    );
    CREATE INDEX IF NOT EXISTS ix_reservation_consumer ON reservations(consumer_id);
    CREATE INDEX IF NOT EXISTS ix_reservation_vendor ON reservations(vendor_id);
    CREATE INDEX IF NOT EXISTS ix_reservation_expiry ON reservations(status,expires_at);
    ''')
    if 'refunded_at' not in [x[1] for x in db.execute('PRAGMA table_info(reservations)')]:
        db.execute('ALTER TABLE reservations ADD COLUMN refunded_at TEXT')
    if db.execute('SELECT COUNT(*) FROM users').fetchone()[0] == 0:
        t = iso()
        vendor1, vendor2, consumer = 'demo-vendor-1', 'demo-vendor-2', 'demo-consumer-1'
        users = [
          (vendor1, 'Maya', 'vendor@echoeats.test', 'vendor', 'Green Oven Bakery', 'Adliya, Manama, Bahrain'),
          (vendor2, 'Omar', 'cafe@echoeats.test', 'vendor', 'Fresh Table Café', 'Seef, Manama, Bahrain'),
          (consumer, 'Demo Consumer', 'consumer@echoeats.test', 'consumer', '', ''),
        ]
        for uid, name, email, role, business, address in users:
            db.execute('INSERT INTO users(id,name,email,phone,password_hash,role,vendor_name,address,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                       (uid,name,email,'+973 3000 0000',hash_pw(DEMO_PASSWORD),role,business,address,t))
        sample=[
          ('Almond Croissant Box','Bakery','🥐','Freshly baked croissants, packed for easy pickup.',6,4.500,3.000,1.500,6,'Vegetarian',vendor1),
          ('Sourdough Surprise Bag','Bakery','🍞','A mixed bag of today’s artisan bread.',8,3.800,2.400,1.000,8,'Vegan',vendor1),
          ('Berry Cheesecake Slice','Desserts','🍰','A slice of berry cheesecake.',5,3.200,2.100,0.900,5,'Vegetarian',vendor1),
          ('Grilled Chicken Bowl','Meals','🥗','Chicken, grains, and seasonal vegetables.',7,5.500,3.700,1.800,7,'High Protein',vendor2),
          ('Iced Latte & Cookie','Drinks','☕','An iced latte paired with a cookie.',9,3.600,2.600,1.200,9,'Vegetarian',vendor2),
          ('Veggie Wrap Duo','Meals','🌯','Two freshly made vegetable wraps.',4,4.000,2.800,1.400,4,'Vegetarian',vendor2),
          ('Fruit & Yogurt Cup','Snacks','🍓','Fresh fruit and yogurt ready to collect.',10,2.500,1.700,0.800,10,'Vegetarian',vendor2),
          ('Chocolate Muffin Pair','Bakery','🧁','Two soft chocolate muffins.',6,3.000,2.000,0.900,6,'Vegetarian',vendor1),
        ]
        for i,(name,category,emoji,description,qty,original,initial,minimum,hours,dietary,vid) in enumerate(sample):
            deadline=iso(now()+timedelta(hours=hours))
            expiry=iso(now()+timedelta(hours=hours+2))
            db.execute('''INSERT INTO listings(id,vendor_id,name,description,category,dietary,emoji,quantity,initial_quantity,original_price,initial_price,min_price,current_price,pickup_deadline,expires_at,pricing_curve,last_price_update,created_at)
                          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                       (f'food-{i+1}',vid,name,description,category,dietary,emoji,qty,qty,original,initial,minimum,initial,deadline,expiry,'linear',t,t))
    db.commit()
    db.close()


def price(food, at=None):
    at=at or now()
    started=dtime(food['created_at']); deadline=dtime(food['pickup_deadline'])
    total=max((deadline-started).total_seconds(),1)
    progress=min(1,max(0,(at-started).total_seconds()/total))
    demand=food['demand_count']/max(food['initial_quantity'],1)
    factor=0.65 if demand>=0.5 else (1.10 if demand<0.15 else 0.90)
    curve=food.get('pricing_curve','linear')
    if curve=='exponential':
        progress=progress**2.2
    elif curve=='stepped':
        progress=int(progress*4)/4
    proposed=round(food['initial_price']*(1-min(0.85,progress*0.75*factor)),3)
    return round(max(food['min_price'],min(food['initial_price'],food['current_price'],proposed)),3)


def settle(db):
    t=iso()
    expired=many(db,"SELECT * FROM reservations WHERE status='pending' AND expires_at<=?",(t,))
    for r in expired:
        db.execute("UPDATE reservations SET status='expired' WHERE id=? AND status='pending'",(r['id'],))
        db.execute("UPDATE listings SET quantity=quantity+? WHERE id=? AND active=1 AND pickup_deadline>? AND expires_at>?",
                   (r['quantity'],r['listing_id'],t,t))
    foods=many(db,"SELECT * FROM listings WHERE active=1 AND pickup_deadline>? AND quantity>0",(t,))
    for food in foods:
        nextprice=price(food)
        if nextprice != food['current_price']:
            db.execute('UPDATE listings SET current_price=?,last_price_update=? WHERE id=?',
                       (nextprice,t,food['id']))


def public_user(u):
    if not u: return None
    return {k:u[k] for k in ('id','name','email','phone','role','vendor_name','address')}


def get_user(request, db, required=True, role=None):
    token=request.cookies.get('echoeats_session','')
    digest=hashlib.sha256(token.encode()).hexdigest() if token else ''
    s=one(db,'SELECT * FROM sessions WHERE token_hash=?',(digest,)) if token else None
    u=one(db,'SELECT * FROM users WHERE id=?',(s['user_id'],)) if s else None
    if s:
        if dtime(s['last_active'])<now()-timedelta(seconds=SESSION_SECONDS):
            db.execute('DELETE FROM sessions WHERE token_hash=?',(digest,));u=None
        else:
            db.execute('UPDATE sessions SET last_active=? WHERE token_hash=?',(iso(),digest))
    if required and not u: fail('Please log in first.',401)
    if role and u and u['role']!=role: fail(f'{role.capitalize()} account required.',403)
    return u


def validate_listing(payload):
    name=str(payload.get('name') or '').strip()
    category=str(payload.get('category') or '').strip()
    if not (1<=len(name)<=110): fail('Food name must be between 1 and 110 characters.')
    if category not in ('Bakery','Meals','Desserts','Drinks','Snacks'): fail('Select a valid food category.')
    try:
        qty=int(payload.get('quantity'))
        if qty != float(payload.get('quantity')): fail('Enter a whole number of portions.')
        original=float(payload.get('original_price'))
        initial=float(payload.get('initial_price'))
        minimum=float(payload.get('min_price'))
    except (TypeError,ValueError):fail('Please enter valid quantities and prices.')
    if not (0<=qty<=9999):fail('Quantity must be between 0 and 9999.')
    if not (0<minimum<initial<=original<=10000):fail('Prices must follow original ≥ starting > minimum > 0.')
    try:
        pickup=dtime(payload['pickup_deadline']); expiry=dtime(payload['expires_at'])
    except (KeyError,TypeError,ValueError):fail('Enter valid pickup and expiration dates.')
    if pickup<=now():fail('Pickup deadline must be in the future.')
    if expiry<pickup:fail('Food expiration cannot be earlier than pickup deadline.')
    if len(str(payload.get('description') or ''))>1500: fail('Food description is too long.')
    if len(str(payload.get('dietary') or ''))>120: fail('Dietary details are too long.')
    if len(str(payload.get('image_url') or ''))>1000: fail('Food image path too long.')
    curve=payload.get('pricing_curve') or 'linear'
    if curve not in ('linear','exponential','stepped'):fail('Invalid pricing curve.')
    return dict(name=name,category=category,description=str(payload.get('description') or '').strip(),
                emoji=str(payload.get('emoji') or '🥡')[:8],dietary=str(payload.get('dietary') or '')[:120],
                image_url=str(payload.get('image_url') or ''),quantity=qty,
                original_price=round(original,3),initial_price=round(initial,3),min_price=round(minimum,3),
                pickup_deadline=iso(pickup),expires_at=iso(expiry),pricing_curve=curve)


class AuthRequest(BaseModel):
    email: str
    password: str


@app.on_event('startup')
def startup():
    init_db()
    # Scheduled expiry independent of an open browser.
    def maintenance():
        while True:
            try:
                with connection(write=True) as db: settle(db)
            except Exception as exc: print('Maintenance:',exc)
            time.sleep(5)
    threading.Thread(target=maintenance,daemon=True,name='echoeats-expiry').start()


@app.get('/api/health')
def health():
    return {'ok':True,'app':'EchoEats','database':'SQLite','payments':'simulated'}


@app.get('/api/session')
def session(request:Request):
    with connection(write=True) as db:
        return public_user(get_user(request,db,required=False))


@app.post('/api/auth/signup')
def signup(request:Request,payload:dict,response:Response):
    email=str(payload.get('email') or '').strip().lower()
    password=str(payload.get('password') or '')
    name=str(payload.get('name') or '').strip()
    phone=str(payload.get('phone') or '').strip()
    role=payload.get('role')
    business=str(payload.get('vendor_name') or '').strip()
    address=str(payload.get('address') or '').strip()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email):fail('Enter a valid email address.')
    if not re.search('[A-Za-z]',password) or not re.search('[0-9]',password) or len(password)<8:fail('Password must have 8+ characters with a letter and a number.')
    if len(name)<2 or len(name)>90:fail('Enter your full name.')
    if role not in ('consumer','vendor'):fail('Choose Consumer or Vendor.')
    if role=='vendor' and (not business or not address):fail('Vendors must enter a business name and pickup address.')
    if len(phone)>40:fail('Phone number is too long.')
    with connection(write=True) as db:
        if one(db,'SELECT id FROM users WHERE email=?',(email,)):fail('An account with this email already exists.',409)
        uid=ident()
        db.execute('INSERT INTO users(id,name,email,phone,password_hash,role,vendor_name,address,created_at) VALUES(?,?,?,?,?,?,?,?,?)',
                   (uid,name,email,phone,hash_pw(password),role,business,address,iso()))
        token=secrets.token_urlsafe(36)
        db.execute('INSERT INTO sessions(token_hash,user_id,last_active) VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,iso()))
    response.set_cookie('echoeats_session',token,max_age=SESSION_SECONDS,httponly=True,samesite='lax',secure=False,path='/')
    return {'session':public_user(dict(id=uid,name=name,email=email,phone=phone,role=role,vendor_name=business,address=address))}


@app.post('/api/auth/login')
def login(payload:AuthRequest,response:Response):
    email=payload.email.strip().lower()
    with connection(write=True) as db:
        u=one(db,'SELECT * FROM users WHERE email=?',(email,))
        if not u:fail('Incorrect email or password.',401)
        if u['locked_until'] and dtime(u['locked_until'])>now():fail('Account temporarily locked after failed attempts. Try again later.',429)
        if not verify_pw(payload.password,u['password_hash']):
            attempts=(u['failed_attempts'] or 0)+1
            locked_until=iso(now()+timedelta(minutes=15)) if attempts>=5 else None
            db.execute('UPDATE users SET failed_attempts=?,locked_until=? WHERE id=?',(attempts,locked_until,u['id']))
            fail_msg='Account temporarily locked for 15 minutes.' if attempts>=5 else 'Incorrect email or password.'
            # Commit failed attempt before returning error.
        else:
            db.execute('UPDATE users SET failed_attempts=0,locked_until=NULL WHERE id=?',(u['id'],))
            token=secrets.token_urlsafe(36)
            db.execute('INSERT INTO sessions(token_hash,user_id,last_active) VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),u['id'],iso()))
            fail_msg=None
    if fail_msg:fail(fail_msg,429 if attempts>=5 else 401)
    response.set_cookie('echoeats_session',token,max_age=SESSION_SECONDS,httponly=True,samesite='lax',secure=False,path='/')
    return {'session':public_user(u)}


@app.post('/api/auth/logout')
def logout(request:Request,response:Response):
    with connection(write=True) as db:
        token=request.cookies.get('echoeats_session','')
        if token: db.execute('DELETE FROM sessions WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),))
    response.delete_cookie('echoeats_session',path='/')
    return {'ok':True}


@app.post('/api/auth/change-password')
def change_password(request:Request,payload:dict):
    old=payload.get('current_password','');new=payload.get('new_password','')
    if len(new)<8 or not re.search('[a-zA-Z]',new) or not re.search('[0-9]',new):fail('New password must contain 8+ characters, a letter, and a number.')
    with connection(write=True) as db:
        u=get_user(request,db)
        if not verify_pw(old,u['password_hash']):fail('Current password incorrect.',403)
        db.execute('UPDATE users SET password_hash=? WHERE id=?',(hash_pw(new),u['id']))
    return {'ok':True}


@app.patch('/api/profile')
def update_profile(request:Request,payload:dict):
    with connection(write=True) as db:
        u=get_user(request,db)
        name=str(payload.get('name',u['name'])).strip()
        phone=str(payload.get('phone',u['phone'])).strip()
        vendor_name=str(payload.get('vendor_name',u['vendor_name'])).strip()
        address=str(payload.get('address',u['address'])).strip()
        if not name or (u['role']=='vendor' and (not vendor_name or not address)):fail('Complete all required fields.')
        db.execute('UPDATE users SET name=?,phone=?,vendor_name=?,address=? WHERE id=?',(name[:90],phone[:40],vendor_name[:100],address[:300],u['id']))
        return public_user(one(db,'SELECT * FROM users WHERE id=?',(u['id'],)))


@app.get('/api/snapshot')
def snapshot(request:Request):
    with connection(write=True) as db:
        settle(db)
        u=get_user(request,db,required=False)
        if u and u['role']=='vendor':
            listings=many(db,"SELECT * FROM listings WHERE active=1 OR vendor_id=? ORDER BY created_at DESC",(u['id'],))
        else:
            listings=many(db,'SELECT * FROM listings WHERE active=1 ORDER BY created_at DESC')
        profiles=many(db,"SELECT id,name,role,vendor_name,address FROM users WHERE role='vendor'")
        if u:
            key='vendor_id' if u['role']=='vendor' else 'consumer_id'
            reservations=many(db,f'SELECT * FROM reservations WHERE {key}=? ORDER BY created_at DESC',(u['id'],))
        else: reservations=[]
        for listing in listings:listing['active']=bool(listing['active'])
        return dict(profiles=profiles,listings=listings,reservations=reservations)


@app.post('/api/listings')
def create_listing(request:Request,payload:dict):
    form=validate_listing(payload)
    with connection(write=True) as db:
        u=get_user(request,db,role='vendor')
        lid=ident();t=iso()
        db.execute('''INSERT INTO listings(id,vendor_id,name,description,category,dietary,emoji,image_url,quantity,initial_quantity,original_price,initial_price,min_price,current_price,demand_count,pickup_deadline,expires_at,pricing_curve,last_price_update,created_at)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
           (lid,u['id'],form['name'],form['description'],form['category'],form['dietary'],form['emoji'],form['image_url'],form['quantity'],form['quantity'],form['original_price'],form['initial_price'],form['min_price'],form['initial_price'],0,form['pickup_deadline'],form['expires_at'],form['pricing_curve'],t,t))
    return {'id':lid}


@app.put('/api/listings/{listing_id}')
def update_listing(listing_id:str,request:Request,payload:dict):
    form=validate_listing(payload)
    with connection(write=True) as db:
        u=get_user(request,db,role='vendor')
        food=one(db,'SELECT * FROM listings WHERE id=? AND vendor_id=?',(listing_id,u['id']))
        if not food:fail('Listing not found.',404)
        if not food['active']:fail('Inactive listings cannot be edited.',409)
        # Initial quantity is adjusted only when extra portions are added.
        initial_qty=food['initial_quantity']+max(0,form['quantity']-food['quantity'])
        nextprice=max(form['min_price'],min(form['initial_price'],food['current_price']))
        db.execute('''UPDATE listings SET name=?,description=?,category=?,dietary=?,emoji=?,image_url=?,quantity=?,initial_quantity=?,original_price=?,initial_price=?,min_price=?,current_price=?,pickup_deadline=?,expires_at=?,pricing_curve=? WHERE id=?''',
          (form['name'],form['description'],form['category'],form['dietary'],form['emoji'],form['image_url'],form['quantity'],initial_qty,form['original_price'],form['initial_price'],form['min_price'],nextprice,form['pickup_deadline'],form['expires_at'],form['pricing_curve'],listing_id))
    return {'ok':True}


@app.delete('/api/listings/{listing_id}')
def deactivate_listing(listing_id:str,request:Request):
    with connection(write=True) as db:
        u=get_user(request,db,role='vendor')
        count=db.execute('UPDATE listings SET active=0 WHERE id=? AND vendor_id=?',(listing_id,u['id'])).rowcount
        if not count:fail('Listing not found.',404)
    return {'ok':True}


@app.post('/api/reservations')
def reserve(request:Request,payload:dict):
    listing_id=str(payload.get('listing_id') or '')
    try:qty=int(payload.get('quantity'))
    except (TypeError,ValueError):fail('Invalid quantity.')
    if qty<1 or qty>9999:fail('Choose a valid quantity.')
    with connection(write=True) as db:
        u=get_user(request,db,role='consumer')
        settle(db)
        food=one(db,'SELECT * FROM listings WHERE id=?',(listing_id,))
        t=iso()
        if not food or not food['active'] or food['pickup_deadline']<=t or food['expires_at']<=t:fail('This food is no longer available.',409)
        if food['quantity']<qty:fail('Not enough portions are available.',409)
        # BEGIN IMMEDIATE locks writes so two consumers cannot oversell the same stock.
        db.execute('UPDATE listings SET quantity=quantity-?,demand_count=demand_count+? WHERE id=?',(qty,qty,listing_id))
        rid=ident()
        db.execute('''INSERT INTO reservations(id,listing_id,vendor_id,consumer_id,consumer_name,quantity,locked_unit_price,status,created_at,expires_at)
                      VALUES(?,?,?,?,?,?,?,?,?,?)''',
                   (rid,listing_id,food['vendor_id'],u['id'],u['name'],qty,food['current_price'],'pending',t,iso(now()+timedelta(seconds=RESERVATION_SECONDS))))
        return one(db,'SELECT * FROM reservations WHERE id=?',(rid,))


def reservation_for(db,id,user,owner):
    r=one(db,'SELECT * FROM reservations WHERE id=?',(id,))
    if not r or r[owner]!=user['id']:fail('Reservation not found.',404)
    return r


@app.post('/api/reservations/{reservation_id}/cancel')
def cancel_reservation(reservation_id:str,request:Request):
    with connection(write=True) as db:
        u=get_user(request,db,role='consumer')
        settle(db)
        r=reservation_for(db,reservation_id,u,'consumer_id')
        if r['status'] not in ('pending','confirmed'):fail('This reservation cannot be cancelled.',409)
        food=one(db,'SELECT * FROM listings WHERE id=?',(r['listing_id'],))
        if r['status']=='confirmed' and (not food or food['pickup_deadline']<=iso()):
            fail('The pickup cancellation deadline has passed.',409)
        db.execute("UPDATE reservations SET status='cancelled',refunded_at=? WHERE id=?",(iso() if r['status']=='confirmed' else None,reservation_id))
        t=iso()
        db.execute('UPDATE listings SET quantity=quantity+? WHERE id=? AND active=1 AND pickup_deadline>? AND expires_at>?',(r['quantity'],r['listing_id'],t,t))
    return {'ok':True,'demo_refund':r['status']=='confirmed'}


@app.post('/api/reservations/{reservation_id}/pay')
def demo_pay(reservation_id:str,request:Request):
    with connection(write=True) as db:
        u=get_user(request,db,role='consumer')
        settle(db)
        r=reservation_for(db,reservation_id,u,'consumer_id')
        if r['status']!='pending' or r['expires_at']<=iso():fail('Reservation expired or already paid.',409)
        code='EE-'+secrets.token_hex(4).upper()
        db.execute("UPDATE reservations SET status='confirmed',pickup_code=?,paid_at=? WHERE id=?",(code,iso(),reservation_id))
        return one(db,'SELECT * FROM reservations WHERE id=?',(reservation_id,))


@app.post('/api/reservations/{reservation_id}/collect')
def collect(reservation_id:str,request:Request):
    with connection(write=True) as db:
        u=get_user(request,db,role='vendor')
        r=reservation_for(db,reservation_id,u,'vendor_id')
        if r['status']!='confirmed':fail('Only confirmed orders can be collected.',409)
        db.execute("UPDATE reservations SET status='collected',collected_at=? WHERE id=?",(iso(),reservation_id))
    return {'ok':True}


@app.post('/api/photos')
def upload_image(request:Request,payload:dict):
    with connection(write=True) as db:
        u=get_user(request,db,role='vendor')
    data=str(payload.get('data') or '')
    match=re.match(r'^data:image/(png|jpeg|webp);base64,([A-Za-z0-9+/=]+)$',data)
    if not match:fail('Upload a PNG, JPG, or WebP photo.')
    try: raw=base64.b64decode(match.group(2),validate=True)
    except Exception:fail('Invalid image data.')
    if len(raw)>2*1024*1024:fail('Photo must be smaller than 2 MB.')
    kind=match.group(1)
    valid={'png':raw.startswith(b'\x89PNG\r\n\x1a\n'),
           'jpeg':raw.startswith(b'\xff\xd8\xff'),
           'webp':raw.startswith(b'RIFF') and raw[8:12]==b'WEBP'}
    if not valid[kind]:fail('Invalid photo format.')
    ext='jpg' if kind=='jpeg' else kind
    filename=f'{uuid.uuid4().hex}.{ext}'
    (UPLOAD/filename).write_bytes(raw)
    return {'url':'/uploads/'+filename}


app.mount('/uploads',StaticFiles(directory=str(UPLOAD)),name='uploads')
app.mount('/assets',StaticFiles(directory=str(ROOT/'assets')),name='assets')
app.mount('/src',StaticFiles(directory=str(ROOT/'src')),name='src')

@app.get('/')
def home():
    return FileResponse(str(ROOT/'index.html'))


if __name__=='__main__':
    import uvicorn
    uvicorn.run(app,host='127.0.0.1',port=8000)
