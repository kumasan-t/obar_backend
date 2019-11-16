from werkzeug.exceptions import InternalServerError, Conflict, NotFound
from sqlalchemy.exc import OperationalError, IntegrityError
from flask import request
from flask_restplus import Namespace, Resource, fields
from obar.models import Product
from obar import db

product_ns = Namespace('product', description='Product related operations')

# TODO: redefine product models according to API input and output requirements
product_model = product_ns.model('Product', {
    'name': fields.String(requred=True,
                          description='Product name',
                          attribute='product_name'),
    'availability': fields.Boolean(required=True,
                                   description='Product availability',
                                   attribute='product_availability'),
    'discount': fields.Float(required=True,
                             description='Product discount',
                             attribute='product_discount'),
    'price': fields.Float(required=True,
                          description='Product description',
                          attribute='product_price'),
    'quantity': fields.Integer(required=True,
                               description='Product quantity',
                               attribute='product_quantity')
})

product_output_model = product_ns.inherit('Product Output', product_model, {
    'code': fields.String(required=True,
                          description='Prodoct identifier',
                          attribute='product_code_uuid')
})


product_put_model = product_ns.model('Product Update', {
    'name': fields.String(requred=False,
                          description='Product name',
                          attribute='product_name'),
    'availability': fields.Boolean(required=False,
                                   description='Product availability',
                                   attribute='product_availability'),
    'discount': fields.Float(required=False,
                             description='Product discount',
                             attribute='product_discount'),
    'price': fields.Float(required=False,
                          description='Product description',
                          attribute='product_price'),
    'quantity': fields.Integer(required=False,
                               description='Product quantity',
                               attribute='product_quantity')
})


@product_ns.route('/')
class ProductListAPI(Resource):

    @product_ns.marshal_list_with(product_output_model)
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
            raise InternalServerError(description='Product table does not exists.')
        return product_list, 200

    @product_ns.doc('post_product')
    @product_ns.response(201, 'Resource created')
    @product_ns.response(500, 'Internal server error')
    @product_ns.response(409, 'Resource already exists')
    @product_ns.expect(product_model, validate=True)
    def post(self):
        """
        Creates a new product
        """
        new_product = Product(product_name=request.json['name'],
                              product_availability=request.json['availability'],
                              product_discount=request.json['discount'],
                              product_price=request.json['price'],
                              product_quantity=request.json['quantity'])
        db.session.add(new_product)
        try:
            db.session.commit()
        except OperationalError:
            raise InternalServerError(description='Product table does not exists.')
        except IntegrityError:
            raise Conflict(description=new_product.__repr__() + ' already exists')
        return {'message': 'Resource created'}, 201


@product_ns.route('/<string:code>')
class ProductAPI(Resource):

    @product_ns.doc('get_product')
    @product_ns.marshal_with(product_output_model)
    @product_ns.response(200, 'Success')
    @product_ns.response(404, 'Product not found')
    def get(self, code):
        """
        Get product data
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound()
        return product, 200

    @product_ns.doc('delete_product')
    @product_ns.response(204, 'Success')
    @product_ns.response(404, 'Product not found')
    def delete(self, code):
        """
        Delete a product
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound()
        db.session.delete(product)
        db.session.commit()
        return '', 204

    @product_ns.doc('delete_product')
    @product_ns.response(204, 'Success')
    @product_ns.response(404, 'Product not found')
    def delete(self, code):
        """
        Delete a product
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound()
        db.session.delete(product)
        db.session.commit()
        return '', 204

    # TODO: redefine models so that an admin user can modify each of this field
    @product_ns.doc('put_product')
    @product_ns.response(204, 'Updated succesfully')
    @product_ns.response(404, 'product not found')
    @product_ns.response(409, 'Conflict in product resources')
    @product_ns.expect(product_put_model, validate=True)
    def put(self, code):
        """
        Edit product data.
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound()
        if 'name' in request.json.keys():
            product.product_name = request.json['name']
        if 'availability' in request.json.keys():
            product.product_availability = request.json['availability']
        if 'price' in request.json.keys():
            product.product_price = request.json['price']
        if 'quantity' in request.json.keys():
            product.product_quantity = request.json['quantity']
        if 'discount' in request.json.keys():
            product.product_discount = request.json['discount']
        try:
            db.session.commit()
        except IntegrityError:
            raise Conflict('Attribute must be unique')
        return '', 204

# TODO: must add image resource to product /code/img and define CRUD for it
