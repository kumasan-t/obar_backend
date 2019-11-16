import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
db = SQLAlchemy()


class Purchase(db.Model):
    """Purchase model
    Represents the purchase from a customer.
    """
    __tablename__ = 'purchase'

    purchase_code_uuid = db.Column(db.String(), primary_key=True)
    purchase_date = db.Column(db.Date())
    purchase_customer_mail_address = db.Column(db.String(), db.ForeignKey('customer.customer_mail_address'))
    purchase_item = db.relationship('PurchaseItem', backref='Purchase')

    def __repr__(self):
        return '<Purchase {}{} >'.format(self.purchase_number, self.purchase_customer_mail_address)

    def __init__(self, purchase_date, purchase_customer_mail_address):
        # Generates a UUID for the Purchase
        self.purchase_code_uuid = uuid.uuid4().hex
        self.purchase_customer_mail_address = purchase_customer_mail_address
        self.purchase_date = purchase_date


class Customer(db.Model):
    """Customer model
    Represents the customer.
    """
    __tablename__ = 'customer'

    customer_mail_address = db.Column(db.String(), primary_key=True)
    customer_pin_hash = db.Column(db.String())  # has to be hashed
    customer_first_name = db.Column(db.String())
    customer_last_name = db.Column(db.String())
    purchase = db.relationship('Purchase', backref='Customer')

    def __init__(self, customer_mail_address, customer_pin_hash, customer_first_name, customer_last_name):
        self.customer_mail_address = customer_mail_address
        self.customer_pin_hash = generate_password_hash(customer_pin_hash)
        self.customer_last_name = customer_last_name
        self.customer_first_name = customer_first_name

    def check_password(self, password):
        """Hash comparator
        Compares password hash in db with the password (hashed) provided by
        the client
        :return boolean: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Customer %r>' % self.customer_mail_address


# TODO: resolve product name conflict in case of upper and lower cases
# TODO: consider adding slugify to product name for name standardization
# For slugify refer to this https://github.com/un33k/python-slugify
class Product(db.Model):

    __tablename__ = 'product'

    product_name = db.Column(db.String(), unique=True)
    product_code_uuid = db.Column(db.String(), primary_key=True)
    product_availability = db.Column(db.Boolean())
    product_price = db.Column(db.Float())
    product_quantity = db.Column(db.Integer())
    product_discount = db.Column(db.Float(), default=0)
    purchaseItem = db.relationship('PurchaseItem', backref='Product')
    productImage = db.relationship('ProductImage', backref='Product', uselist=False)

    def __init__(self, product_name, product_availability, product_discount, product_price, product_quantity):
        # Generates a UUID for the the product
        self.product_code_uuid = uuid.uuid4().hex
        self.product_name = product_name
        self.product_availability = product_availability
        self.product_price = product_price
        self.product_quantity = product_quantity
        self.product_discount = product_discount

    def __repr__(self):
        return '<Product {} {}>'.format(self.product_name, self.product_code_uuid)


class PurchaseItem(db.Model):

    __tablename__ = 'purchase_item'

    purchase_item_uuid = db.Column(db.String(), primary_key=True)
    purchase_item_quantity = db.Column(db.Integer())
    purchase_item_product_code_uuid = db.Column(db.String(), db.ForeignKey('product.product_code_uuid'))
    purchase_item_purchase_code_uuid = db.Column(db.String(), db.ForeignKey('purchase.purchase_code_uuid'))

    def __init__(self, purchase_item_quantity, purchase_item_product_code_uuid, purchase_item_purchase_code_uuid):
        # Generates a UUID for the Purchase Item
        self.purchase_item_uuid = uuid.uuid4().hex
        self.purchase_item_purchase_code_uuid = purchase_item_purchase_code_uuid
        self.purchase_item_product_code_uuid = purchase_item_product_code_uuid
        self.purchase_item_quantity = purchase_item_quantity

    def __repr__(self):
        return '<PurchaseItem {}{}>'.format(self.purchase_item_number, self.purchase_purchase_item)


class ProductImage(db.Model):
    """Product Image model
    Represents the relative path of images stored for each product
    """
    __tablename__ = 'product_image'

    product_image_binary = db.Column(db.LargeBinary())
    product_image_filename = db.Column(db.String(), primary_key=True)
    product_image_product_code_uuid = db.Column(db.String(), db.ForeignKey('product.product_code_uuid'))
    product = db.relationship('Product', backref='ProductImage')

    def __repr__(self):
        return '<ProductImage {}>'.format(self.product_image_filename)
