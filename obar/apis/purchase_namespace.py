from flask_restplus import Namespace, Resource, fields
from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import InternalServerError, NotFound

from obar.models import Purchase
from .decorator import admin_token_required, customer_token_required

authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

purchase_ns = Namespace('purchase', description='Purchase related operations', authorizations=authorizations)

purchase_model = purchase_ns.model('Purchase', {
    'gifted': fields.Boolean(required=True,
                             description='Gifted purchase',
                             attribute='purchase_gifted'),
    'date': fields.DateTime(required=True,
                            description='Purchase date',
                            attribute='purchase_date'),
    'mail_address': fields.String(required=True,
                                  description='Purchase owner',
                                  attribute='purchase_customer_mail_address')
})

purchase_output_model = purchase_ns.inherit('Purchase Output', purchase_model, {
    'code': fields.String(required=True,
                          description='Purchase number',
                          attribute='purchase_code_uuid')
})


@purchase_ns.route('')
class PurchaseListAPI(Resource):

    @admin_token_required
    @purchase_ns.marshal_list_with(purchase_output_model)
    @purchase_ns.response(200, 'Return a list of purchases')
    @purchase_ns.response(500, 'Internal server error')
    @purchase_ns.doc('get_purchase_list', security='JWT')
    def get(self):
        """
        Returns a list of Purchases
        """
        try:
            purchase_list = Purchase.query.all()
        except OperationalError:
            raise InternalServerError(description='Purchase table does not exists')
        return purchase_list, 200


@purchase_ns.route('/<string:purchase_uuid>')
class PurchaseAPI(Resource):
    @customer_token_required
    @purchase_ns.doc('get_purchase', security='JWT')
    @purchase_ns.response(200, 'Return a purchase')
    @purchase_ns.response(404, 'The resource cannot be found')
    @purchase_ns.marshal_with(purchase_model)
    def get(self, purchase_uuid):
        purchase = Purchase.query.filter_by(purchase_code_uuid=purchase_uuid).first()
        if purchase is None:
            raise NotFound()
        return purchase, 200
