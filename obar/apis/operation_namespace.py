from flask_restplus import Resource, Namespace, fields
from obar.models import Customer, Purchase, PurchaseItem, Product
from flask import request
from obar.models import db
from werkzeug.exceptions import NotFound, UnprocessableEntity
from datetime import datetime as dt
from .decorator.auth_decorator import customer_token_required

authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

operation_ns = Namespace('operation', description='Common operations', authorizations=authorizations)

purchase_details_model = operation_ns.model('Product details', {
    'product_code': fields.String(required=True,
                                  description='Product code'),
    'purchase_quantity': fields.Integer(required=True,
                                        description='Item quantity')
})

perform_purchase_model = operation_ns.model('Purchase Order', {
    'customer_mail_address': fields.String(required=True,
                                           description='Customer identifier'),
    'purchase_details': fields.List(fields.Nested(purchase_details_model))
})


@operation_ns.route('/purchaseProducts')
class OperationAPI(Resource):

    @operation_ns.doc('post_purchase_products', security='JWT')
    @operation_ns.expect(perform_purchase_model, validate=True)
    @customer_token_required
    def post(self):
        """
        Performs a purchase operation
        """
        customer = Customer.query.filter_by(customer_mail_address=request.json['customer_mail_address']).first()
        purchase = Purchase(purchase_date=dt.now(),
                            purchase_customer_mail_address=customer.customer_mail_address)

        if customer is None:
            raise NotFound(description='Resource ' + customer.__repr__() + ' is not found')

        # check if the product is requested more than once
        product_list = set()
        for details in request.json['purchase_details']:
            # adds the product to a set to later check if the product
            # appears more than once in the purchase_details
            if details['purchase_quantity'] <= 0:
                raise UnprocessableEntity('Purchase quantity cannot be <= 0')
            product_list.add(details['product_code'])

        # If length of set and received entries are different then
        # it means some products shows up twice in the list,
        # raise 422 HTTP error
        if len(product_list) != len(request.json['purchase_details']):
            raise UnprocessableEntity('A product has been submitted twice')

        # adds the purchase to session
        db.session.add(purchase)
        for details in request.json['purchase_details']:
            product = Product.query.filter_by(product_code_uuid=details['product_code']).first()
            if not product.product_availability:
                db.session.remove()
                raise UnprocessableEntity('Unavailable product selected')
            if product.product_quantity <= 0:
                db.session.remove()
                raise UnprocessableEntity('Product out of stock')
            if product.product_quantity < details['purchase_quantity']:
                db.session.remove()
                raise UnprocessableEntity('Too much quantity requested')
            # update the product quantity
            product.product_quantity = product.product_quantity - details['purchase_quantity']
            # create a new association object between a purchase and a product
            purchase_item = PurchaseItem(purchase_item_product_code_uuid=product.product_code_uuid,
                                         purchase_item_purchase_code_uuid=purchase.purchase_code_uuid,
                                         purchase_item_quantity=details['purchase_quantity'])
            db.session.add(purchase_item)
        db.session.commit()
        return '', 200
