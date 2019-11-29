import base64

from flask import request
from flask_restplus import Namespace, Resource, fields
from sqlalchemy.exc import OperationalError, IntegrityError
from werkzeug.exceptions import InternalServerError, NotFound, BadRequest

from obar import db
from obar.models import Product, ProductImage
from .decorator import admin_token_required
from .marshal.fields import product_image_fields, product_put_fields, product_post_fields

authorizations = {
    "JWT": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization"
    }
}

product_ns = Namespace('product', description='Product related operations', authorizations=authorizations)

# TODO: move models to fields.py
product_model = product_ns.model('Product', product_post_fields)

product_output_model = product_ns.inherit('Product Output', product_model, {
    'code': fields.String(required=True,
                          description='Prodoct identifier',
                          attribute='product_code_uuid')
})

product_put_model = product_ns.model('Product Update', product_put_fields)

product_image_model = product_ns.model('Product Image', product_image_fields)


@product_ns.route('/')
class ProductListAPI(Resource):

    @product_ns.response(200, 'Return a list of products')
    @product_ns.response(500, 'Internal server error')
    @product_ns.doc('get_product_list')
    @product_ns.marshal_list_with(product_output_model)
    def get(self):
        """
        Returns a list of Product
        """
        try:
            product_list = Product.query.all()
        except OperationalError:
            raise InternalServerError(description='Product table does not exists.')
        return product_list, 200

    @admin_token_required
    @product_ns.doc('post_product', security='JWT')
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
                              product_quantity=request.json['quantity'],
                              product_location_id=request.json['location_id'])
        db.session.add(new_product)
        try:
            db.session.commit()
        except OperationalError:
            raise InternalServerError(description='Product table does not exists.')
        except IntegrityError:
            raise BadRequest('Causes may be: name not unique, non existent location ID')
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

    @admin_token_required
    @product_ns.doc('delete_product', security='JWT')
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
    @admin_token_required
    @product_ns.doc('put_product', security='JWT')
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
        if 'location_id' in request.json.keys():
            product.product_location_id = request.json['location_id']
        try:
            db.session.commit()
        except IntegrityError:
            raise BadRequest('Causes may be: name not unique, non existent location ID')
        return '', 204


@product_ns.route('/<string:code>/img')
class ProductImageAPI(Resource):

    @product_ns.doc('get_product_image')
    @product_ns.response(200, 'Success')
    @product_ns.response(404, 'Product not Found')
    @product_ns.response(404, 'Image not Found')
    @product_ns.marshal_with(product_image_model)
    def get(self, code):
        """
        Get product image data
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound('Product not found')
        image = product.productImage
        if image is None:
            raise NotFound('Image not found')
        response = {
            'filename': image.product_image_filename,
            'file_base64': base64.b64encode(image.product_image_binary).decode('ascii')
        }
        return response, 200

    @admin_token_required
    @product_ns.doc('post_product_image', security='JWT')
    @product_ns.response(201, 'Resource created')
    @product_ns.expect(product_image_model, validate=True)
    def post(self, code):
        """
        Post new product image data
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound()
        image = ProductImage(product_image_product_code_uuid=code,
                             product_image_filename=request.json['filename'],
                             product_image_binary=base64.b64decode(request.json['file_base64']))
        db.session.add(image)
        db.session.commit()

        return '', 201

    @admin_token_required
    @product_ns.doc('put_product_image', security='JWT')
    @product_ns.response(204, 'Updated successfully')
    @product_ns.response(404, 'Product not found')
    @product_ns.response(404, 'Image not found')
    @product_ns.expect(product_image_model)
    def put(self, code):
        """
        Update product image
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound('Product not found')
        image = product.productImage
        if image is None:
            raise NotFound('Image not found')

        if 'filename' in request.json:
            image.product_image_filename = request.json['filename']
        if 'file_base64' in request.json:
            image.product_image_binary = base64.b64decode(request.json['file_base64'])

        db.session.commit()
        return '', 204

    @admin_token_required
    @product_ns.doc('delete_product_image', security='JWT')
    @product_ns.response(204, 'Success')
    @product_ns.response(404, 'Product not found')
    @product_ns.response(404, 'Image not found')
    def delete(self, code):
        """
        Delete product image
        """
        product = Product.query.filter_by(product_code_uuid=code).first()
        if product is None:
            raise NotFound('%s not found')
        image = product.productImage
        if image is None:
            raise NotFound('%s not found')

        db.session.delete(image)
        db.session.commit()

        return '', 204
