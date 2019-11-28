from flask_restplus import Namespace, Resource, fields
from sqlalchemy.exc import OperationalError
from werkzeug.exceptions import InternalServerError

from obar.models import Purchase

purchase_ns = Namespace('purchase', description='Purchase related operations')

purchase_model = purchase_ns.model('Purchase', {
    'date': fields.Date(required=True,
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


@purchase_ns.route('/')
class PurchaseListAPI(Resource):

    @purchase_ns.marshal_list_with(purchase_output_model)
    @purchase_ns.response(200, 'Return a list of purchases')
    @purchase_ns.response(500, 'Internal server error')
    @purchase_ns.doc('get_purchase_list')
    def get(self):
        """
        Returns a list of Purchases
        """
        try:
            purchase_list = Purchase.query.all()
        except OperationalError:
            raise InternalServerError(description='Purchase table does not exists')
        return purchase_list, 200
