import os
import sys
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'openbazar.settings')

import django
from django.test import Client

def main():
    try:
        django.setup()
        client = Client()
        resp = client.get('/dashboard/', HTTP_HOST='127.0.0.1')
        print('STATUS:', resp.status_code)
        if resp.status_code in (301,302,303,307,308):
            print('REDIRECT TO:', resp.get('Location'))
        content = resp.content.decode('utf-8', errors='replace')
        print('CONTENT_SNIPPET:\n')
        print(content[:4000])
    except Exception:
        traceback.print_exc()

if __name__ == '__main__':
    main()
