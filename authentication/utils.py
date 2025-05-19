import jwt
import hashlib
from datetime import datetime, timedelta
from django.conf import settings

def generateTokens(user):
    refresh_token = jwt.encode({   
                    "username": user.get('username', ''), 
                    "exp": datetime.utcnow() + timedelta(days=7) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    access_token = jwt.encode({   
                    "username": user.get('username', ''), 
                    "exp": datetime.utcnow() + timedelta(minutes=60) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    return refresh_token, access_token 

def generateTokensUser(user):
    refresh_token = jwt.encode({   
                    "username": user.username, 
                    "exp": datetime.utcnow() + timedelta(days=7) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    access_token = jwt.encode({   
                    "username": user.username, 
                    "exp": datetime.utcnow() + timedelta(minutes=60) 
                }, settings.JWT_SECRET_KEY, algorithm='HS256')
    return refresh_token, access_token 

def hash_password(password):
    salt = "random string to make the hash more secure"
    salted_password = password + salt
    hashed_password = hashlib.sha256(salted_password.encode('utf-8')).hexdigest()
    return hashed_password

def check_password(user, password):
    return hash_password(password) == user.password_hash

def updateRefreshToken(user, refresh_token):
    user.refresh_token = refresh_token
    user.save()