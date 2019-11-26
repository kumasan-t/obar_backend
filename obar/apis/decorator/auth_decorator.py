from obar.models import Customer
from functools import wraps
from flask import request


def customer_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            data = Customer.decode_auth_token(token)
            if data['status'] == 'fail':
                return data, 401
        if not token:
            return {'message': 'Token is missing'}, 401
        return f(*args, **kwargs)
    return decorated


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            data = Customer.decode_auth_token(token)
            if data['status'] == 'fail':
                return data, 401
            elif not data['admin']:
                return {'message': 'Admin token required, please login with an admin account'}, 401
        if not token:
            return {'message': 'Token is missing'}, 401
        return f(*args, **kwargs)
    return decorated
