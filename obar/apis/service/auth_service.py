from obar.models import Customer
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
