import re
from flask import session, redirect, url_for, request
from functools import wraps
from dotenv import load_dotenv
from os import getenv
from pymongo import MongoClient
from bson import ObjectId

load_dotenv()
client = MongoClient(getenv('MONGO_URL'))
users = client['users']

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "id" not in session:
            return redirect(url_for('login'))
        
        user = users['login_info'].find_one({'_id': ObjectId(session['id'])})

        if 'role' not in user or user['role'] != 'admin':
            return redirect(url_for('index'))
        
        return func(*args, **kwargs)
    return wrapper


def is_valid_email(email):
    # Regular expression for validating an email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if re.match(email_regex, email):
        return True
    return False

def get_client_ip():
    if not request.environ.get('HTTP_X_FORWARDED_FOR'):
        return(request.environ['REMOTE_ADDR'])
    else:
        return(request.environ['HTTP_X_FORWARDED_FOR']) # if behind a proxy