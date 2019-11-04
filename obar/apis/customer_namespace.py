from flask import request, current_app
from flask_restplus import Namespace, Resource, fields

from obar.models import Customer
from obar import db


customer_ns = Namespace('customer', description='Customer related operations')

model = customer_ns.model('Customer', {
    'mail_address': fields.String(required=True,
                                  description='The customer mail address',
                                  attribute='customer_mail_address'),
    'pin': fields.String(required=True,
                         description='The customer PIN',
                         attribute='customer_pin'),
    'first_name': fields.String(required=True,
                                description='The customer first name',
                                attribute='customer_first_name'),
    'last_name': fields.String(required=True,
                               description='The customer last name',
                               attribute='customer_last_name')
})


@customer_ns.route('/')
class CustomerListAPI(Resource):
    @customer_ns.doc('get_customer_list')
    @customer_ns.marshal_list_with(model)
    def get(self):
        return Customer.query.all(), 200

    @customer_ns.doc('post_customer')
    @customer_ns.expect(model, validate=True)
    @customer_ns.marshal_with(model)
    def post(self):
        new_customer = Customer(customer_mail_address=request.json['mail_address'],
                                customer_first_name=request.json['first_name'],
                                customer_last_name=request.json['last_name'])
        '''Surround with try and catch!!'''
        new_customer.set_password(request.json['pin'])
        db.session.add(new_customer)
        db.session.commit()
        current_app.logger.info(new_customer.__repr__() + ' added to database.')
        response_object = {
            'status': 'success',
            'message': 'Successfully inserted customer.'
        }
        return response_object, 200


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
