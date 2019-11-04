from flask import request, current_app
from flask_restplus import Namespace, Resource, fields, abort
from sqlalchemy.exc import OperationalError, IntegrityError
from werkzeug.exceptions import Conflict, InternalServerError
from obar.models import Customer
from obar import db


customer_ns = Namespace('customer', description='Customer related operations')

model = customer_ns.model('Customer', {
    'mail_address': fields.String(required=True,
                                  description='The customer mail address',
                                  attribute='customer_mail_address'),
    'pin': fields.String(required=True,
                         description='The customer PIN',
                         attribute='customer_pin_hash'),
    'first_name': fields.String(required=True,
                                description='The customer first name',
                                attribute='customer_first_name'),
    'last_name': fields.String(required=True,
                               description='The customer last name',
                               attribute='customer_last_name')
})


@customer_ns.errorhandler(IntegrityError)
def handle_operational_exception(self):
    return {'message': 'What you want'}, 400


@customer_ns.route('/')
class CustomerListAPI(Resource):

    @customer_ns.doc('get_customer_list')
    @customer_ns.response(500, 'Internal server error')
    @customer_ns.marshal_list_with(model)
    def get(self):
        customer_list = None
        try:
            customer_list = Customer.query.all()
        except OperationalError:
            raise InternalServerError(description='Customer table does not exists.')
        return customer_list

    @customer_ns.doc('post_customer')
    @customer_ns.response(200, 'Success')
    @customer_ns.response(409, 'The resource already exists')
    @customer_ns.response(500, 'Internal server error')
    @customer_ns.expect(model, validate=True)
    def post(self):
        new_customer = Customer(customer_mail_address=request.json['mail_address'],
                                customer_first_name=request.json['first_name'],
                                customer_last_name=request.json['last_name'])
        '''Surround with try and catch!!'''
        new_customer.set_password(request.json['pin'])
        print(new_customer.customer_pin_hash)
        db.session.add(new_customer)
        try:
            db.session.commit()
        except OperationalError:
            raise InternalServerError(description='Customer table does not exists.')
        except IntegrityError:
            raise Conflict(description=new_customer.__repr__() + ' already exists')
        current_app.logger.info(new_customer.__repr__() + ' added to database.')
        return 200


@customer_ns.route('/<string:id>')
class CustomerAPI(Resource):

    @customer_ns.doc('get_customer')
    @customer_ns.marshal_with(model)
    def get(self, id):
        return Customer.query.filter_by(customer_mail_address=id).first()

    @customer_ns.doc('del_customer')
    @customer_ns.marshal_with(model)
    def delete(self, id):
        db.session.delete(Customer.query.filter_by(customer_mail_address=id).first())
        db.session.commit()
        return
