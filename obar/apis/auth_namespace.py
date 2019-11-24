from flask_restplus import Namespace, Resource
from flask import request
from .service.auth_service import login_customer, logout_customer
from .marshal.fields import customer_login_fields

auth_ns = Namespace('auth', description='authentication related operations')
user_auth_model = auth_ns.model('Auth Details', customer_login_fields)


@auth_ns.route('/login')
class CustomerLoginAPI(Resource):

    @auth_ns.doc('customer_login')
    @auth_ns.expect(user_auth_model, validate=True)
    def post(self):
        post_data = request.json
        return login_customer(post_data)


@auth_ns.route('/logout')
class CustomerLogoutAPI(Resource):

    @auth_ns.doc('customer_logout')
    def post(self):
        # get auth token
        auth_header = request.headers.get('Authorization')
        print(auth_header)
        return logout_customer(data=auth_header)