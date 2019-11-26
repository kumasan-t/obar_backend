from obar.models import Customer, db
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Conflict
from .blacklist_service import save_token


def login_customer(data):
    try:
        customer = Customer.query.filter_by(customer_mail_address=data['mail_address']).first()
        if customer and customer.check_password(pin=str(data['pin'])):
            auth_token = customer.encode_auth_token()
            if auth_token:
                response_object = {
                    'status': 'success',
                    'message': 'Succesfully logged in',
                    'Authorization': auth_token.decode()
                }
                return response_object, 200
        else:
            response_object = {
                'status': 'fail',
                'message': 'email or pin does not match'
            }
            return response_object, 401
    except Exception as e:
        print(e)
        response_object = {
            'status': 'fail',
            'message': 'Try again'
        }
        return response_object, 500


def logout_customer(data):
    auth_token = data
    if auth_token:
        resp = Customer.decode_auth_token(auth_token)
        if resp['status'] == 'success':
            # mark the token as blacklisted
            return save_token(token=auth_token)
        else:
            return resp, 401
    else:
        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token'
        }
        return response_object, 403


def register_admin_customer():
    admin = Customer(customer_mail_address='admin@test.com',
                     customer_first_name='admin',
                     customer_last_name='admin',
                     customer_pin_hash='12345'
                     )
    admin.customer_is_admin = True
    db.session.add(admin)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.remove()
        raise Conflict(description=admin.__repr__() + ' already exists')
    response = {
        'mail_address': admin.customer_mail_address,
        'pin': 12345,
        'message': 'Login to get an admin token'
    }
    return response, 200
