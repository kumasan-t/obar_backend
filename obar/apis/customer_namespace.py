from flask import request, current_app
from flask_restplus import Namespace, Resource, fields
from sqlalchemy.exc import OperationalError, IntegrityError
from werkzeug.exceptions import Conflict, InternalServerError, NotFound, UnprocessableEntity, Unauthorized

from obar import db
from obar.models import Customer
from .decorator import admin_token_required, customer_token_required

authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

customer_ns = Namespace('customer', description='Customer related operations', authorizations=authorizations)

# Models defined for marshaling of input requests and responses.
# TODO: create a custom Email field that validates email addresses
# Refer to this for custom fields https://blog.fossasia.org/better-fields-and-validation-in-flask-restplus/

customer_input_model = customer_ns.model('Customer Input', {
    'mail_address': fields.String(required=True,
                                  description='Customer mail address',
                                  attribute='customer_mail_address'),
    'pin': fields.Integer(required=True,
                          description='Customer PIN',
                          attribute='customer_pin_hash'),
    'first_name': fields.String(required=True,
                                description='Customer first name',
                                attribute='customer_first_name'),
    'last_name': fields.String(required=True,
                               description='Customer last name',
                               attribute='customer_last_name')
})

customer_output_model = customer_ns.model('Customer Output', {
    'mail_address': fields.String(required=True,
                                  description='Customer mail address',
                                  attribute='customer_mail_address'),
    'first_name': fields.String(required=True,
                                description='Customer first name',
                                attribute='customer_first_name'),
    'last_name': fields.String(required=True,
                               description='Customer last name',
                               attribute='customer_last_name')
})

customer_put_model = customer_ns.model('Customer Update', {
    'pin': fields.Integer(required=False,
                          description='Customer PIN',
                          attribute='customer_pin_hash'),
    'first_name': fields.String(required=False,
                                description='Customer first name',
                                attribute='customer_first_name'),
    'last_name': fields.String(required=False,
                               description='Customer last name',
                               attribute='customer_last_name')
})


@customer_ns.route('/')
class CustomerListAPI(Resource):

    @admin_token_required
    @customer_ns.doc('get_customer_list', security='JWT')
    @customer_ns.response(200, 'Returns a list of customers')
    @customer_ns.response(500, 'Internal server error')
    @customer_ns.marshal_list_with(customer_output_model)
    def get(self):
        """
        Returns a list of customers.
        """
        customer_list = None
        try:
            customer_list = Customer.query.all()
        except OperationalError:
            raise InternalServerError(description='Customer table does not exists.')
        return customer_list, 200

    @admin_token_required
    @customer_ns.doc('post_customer', security='JWT')
    @customer_ns.response(201, 'Resource created')
    @customer_ns.response(409, 'The resource already exists')
    @customer_ns.response(500, 'Internal server error')
    @customer_ns.expect(customer_input_model, validate=True)
    def post(self):
        """
        Creates a new customer.
        """
        if not (0 <= request.json["pin"] <= 99999):
            raise UnprocessableEntity("The PIN must be of 5 digits")
        new_customer = Customer(customer_mail_address=request.json['mail_address'],
                                customer_first_name=request.json['first_name'],
                                customer_last_name=request.json['last_name'],
                                customer_pin_hash=str(request.json['pin']))
        print(new_customer.customer_pin_hash)
        db.session.add(new_customer)
        try:
            db.session.commit()
        except OperationalError:
            db.session.remove()
            raise InternalServerError(description='Customer table does not exists.')
        except IntegrityError:
            db.session.remove()
            raise Conflict(description=new_customer.__repr__() + ' already exists')
        current_app.logger.info(new_customer.__repr__() + ' added to database.')
        return {'message': 'Resource created'}, 201


@customer_ns.route('/<string:mail_address>')
class CustomerAPI(Resource):

    @customer_token_required
    @customer_ns.doc('get_customer', security='JWT')
    @customer_ns.marshal_with(customer_output_model)
    @customer_ns.response(200, 'Success')
    @customer_ns.response(404, 'Customer not found')
    def get(self, mail_address):
        """
        Get customer data.
        """
        token = request.headers['Authorization']
        data = Customer.decode_auth_token(token)
        if not data['admin'] and data['customer'] != mail_address:
            raise Unauthorized()
        customer = Customer.query.filter_by(customer_mail_address=mail_address).first()
        if customer is None:
            raise NotFound()
        return customer, 200

    @admin_token_required
    @customer_ns.doc('del_customer', security='JWT')
    @customer_ns.response(204, description='No content')
    @customer_ns.response(404, 'Customer not found')
    def delete(self, mail_address):
        """
        Delete customer data.
        """
        customer = Customer.query.filter_by(customer_mail_address=mail_address).first()
        if customer is None:
            raise NotFound()
        db.session.delete(customer)
        db.session.commit()
        return '', 204

    @customer_token_required
    @customer_ns.doc('put_customer', security='JWT')
    @customer_ns.response(204, 'Updated succesfully')
    @customer_ns.response(404, 'Customer not found')
    @customer_ns.expect(customer_put_model, validate=True)
    def put(self, mail_address):
        """
        Edit customer data.
        """
        token = request.headers['Authorization']
        data = Customer.decode_auth_token(token)
        if not data['admin'] and data['customer'] != mail_address:
            raise Unauthorized()
        customer = Customer.query.filter_by(customer_mail_address=mail_address).first()
        if customer is None:
            raise NotFound()
        if 'pin' in request.json.keys():
            if not (0 <= request.json["pin"] <= 99999):
                raise UnprocessableEntity("The PIN must be 5 digits")
            customer.set_password(str(request.json['pin']))
        if 'first_name' in request.json.keys():
            customer.customer_first_name = request.json['first_name']
        if 'last_name' in request.json.keys():
            customer.customer_last_name = request.json['last_name']
        db.session.commit()
        return '', 204
