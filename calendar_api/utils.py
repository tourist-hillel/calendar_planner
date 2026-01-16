import jwt
from django.conf import settings
from datetime import datetime, timedelta, timezone

JWT_SETTINGS = getattr(settings, 'SIMPLE_JWT', {})
ACCESS_TOKEN_LIFETIME = JWT_SETTINGS.get('ACCESS_TOKEN_LIFETIME', timedelta(minutes=2))
REFRESH_TOKEN_LIFETIME = JWT_SETTINGS.get('REFRESH_TOKEN_LIFETIME', timedelta(minutes=4))

def create_access_token(user):
    return jwt.encode({
        'user_id': user.id,
        'cell_phone': user.cell_phone,
        'is_staff': user.is_staff,
        'exp': datetime.now(timezone.utc) + ACCESS_TOKEN_LIFETIME,
        'iat': datetime.now(timezone.utc),
        'token_type': 'access'
    }, settings.SECRET_KEY, algorithm='HS256')

def create_refresh_token(user):
    return jwt.encode({
        'user_id': user.id,
        'exp': datetime.now(timezone.utc) + REFRESH_TOKEN_LIFETIME,
        'iat': datetime.now(timezone.utc),
        'token_type': 'refresh'
    }, settings.SECRET_KEY, algorithm='HS256')