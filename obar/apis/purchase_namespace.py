from werkzeug.exceptions import InternalServerError, Conflict, NotFound
from sqlalchemy.exc import OperationalError, IntegrityError
from flask import request
from flask_restplus import Namespace, Resource, fields
from obar.models import Purchase
from obar import db

purchase_ns = Namespace('purchase', description='Purchase related operations')

purchase_model = purchase_ns.model('Purchase', {
    'date': fields.Date(required=True,
                        description='Purchase date',
                        attribute='purchase_date'),
    'customer_mail_address': fields.String(required=True,
                                           description='Purchase owner',
                                           attribute='purchase_customer_mail_address')
})

purchase_output_model = purchase_ns.inherit('Purchase Output', purchase_model, {
    'number': fields.Integer(required=True,
                                      description='Purchase number',
                                      attribute='purchase_number')
})

