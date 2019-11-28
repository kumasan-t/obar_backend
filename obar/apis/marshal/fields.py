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
