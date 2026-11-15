"""One command to start the full EchoEats website with real local database."""
from pathlib import Path
import os
import uvicorn
os.chdir(Path(__file__).resolve().parent)
if __name__=='__main__':
    print('\nEchoEats ready at http://127.0.0.1:8765')
    print('Demo consumer: consumer@echoeats.test / Demo12345!')
    print('Demo vendor: vendor@echoeats.test / Demo12345!\n')
    uvicorn.run('backend.main:app',host='127.0.0.1',port=8765,reload=False)
