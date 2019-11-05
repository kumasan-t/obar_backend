from werkzeug.exceptions import InternalServerError, Conflict
from sqlalchemy.exc import OperationalError, IntegrityError
from flask import request
from flask_restplus import Namespace, Resource, fields
from obar.models import Product
from obar import db

product_ns = Namespace('product', description='Product related operations')

# TODO: redefine product models according to API input and output requirements
# TODO: change price field to float
product_model = product_ns.model('Product', {
    'number': fields.Integer(required=True,
                             description='Product number',
                             attribute='product_number'),
    'availability': fields.Boolean(required=True,
                                   description='Product availability',
                                   attribute='product_availability'),
    'discount': fields.Float(required=True,
                             description='Product discount',
                             attribute='product_discount'),
    'price': fields.Integer(required=True,
                            description='Product description',
                            attribute='product_price'),
    'unit': fields.Integer(required=True,
                           description='Product unit',
                           attribute='product_unit')
})


@product_ns.route('/')
class ProductListAPI(Resource):

    @product_ns.marshal_list_with(product_model)
    @product_ns.response(200, 'Return a list of products')
    @product_ns.response(500, 'Internal server error')
    @product_ns.doc('get_product_list')
    def get(self):
        """
        Returns a list of Product
        """
        try:
            product_list = Product.query.all()
        except OperationalError:
            raise InternalServerError(description='Customer table does not exists.')
        return product_list, 200

    @product_ns.doc('post_product')
    @product_ns.response(201, 'Resource created')
    @product_ns.response(500, 'Internal server error')
    @product_ns.response(409, 'Resource already exists')
    @product_ns.expect(product_model)
    def post(self):
        """
        Creates a new product
        """
        new_product = Product(product_number=request.json['number'],
                              product_availability=request.json['availability'],
                              product_discount=request.json['discount'],
                              product_price=request.json['price'],
                              product_unit=request.json['unit'])
        db.session.add(new_product)
        try:
            db.session.commit()
        except OperationalError:
            raise InternalServerError(description='Product table does not exists.')
        except IntegrityError:
            raise Conflict(description=new_product.__repr__() + ' already exists')
        return {'message': 'Resource created'}, 201

