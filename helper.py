import re

def check_email(email):
    pattern = "\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*'"
    if re.match(pattern, email):
        return True
    else:
        return False

