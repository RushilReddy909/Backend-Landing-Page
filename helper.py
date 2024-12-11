import re
from flask import session, redirect, url_for
from functools import wraps

def login_required(func):
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if 'id' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated_func

def check_email(email):
    pattern = "\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*'"
    if re.match(pattern, email):
        return True
    else:
        return False

