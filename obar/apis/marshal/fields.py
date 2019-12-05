from flask_restplus import fields

product_image_fields = {
    'filename': fields.String(required=False,
                              description='Image filename'),
    'file_base64': fields.String(required=False,
                                 description='Base64 image representation')
}

customer_login_fields = {
    'mail_address': fields.String(required=True,
                                  description='Customer email address'),
    'pin': fields.Integer(required=True,
                          description='Customer pin')
}

site_fields = {
    'id': fields.Integer(description='Site ID',
                         attribute='site_id'),
    'address': fields.String(description='Site address',
                             attribute='site_address')
}

site_fields_post = {
    'address': fields.String(required=True,
                             description='Site address')
}

product_put_fields = {
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
                               attribute='product_quantity'),
    'location_id': fields.Integer(required=False,
                                  description='Product location',
                                  attribute='product_location_id')
}

product_post_fields = {
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
                               attribute='product_quantity'),
    'location_id': fields.Integer(required=True,
                                  description='Product location',
                                  attribute='product_location_id')
}

purchase_item_fields = {
    'uuid': fields.String(description='Purchase item UUID',
                          attribute='purchase_item_uuid'),
    'quantity': fields.Integer(description='Purchase item quantity',
                               attribute='purchase_item_quantity'),
    'price': fields.Float(description='Purchase item price',
                          attribute='purchase_item_price')
}

operation_purchase_leaderboard_fields = {
    'customer': fields.String(description='Customer mail address'),
    'purchases': fields.Integer(description='Number of purchases')
}

operation_best_selling_fields = {
    'name': fields.String(requred=False,
                          description='Product name',
                          attribute='product_name'),
    'uuid': fields.String(description='Product UUID',
                          attribute='product_code_uuid'),
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
                               attribute='product_quantity'),
    'location_id': fields.Integer(required=False,
                                  description='Product location',
                                  attribute='product_location_id'),
    'num_of_purchases': fields.Integer(description='Number of purchases',
                                       attribute='purchases')

}
