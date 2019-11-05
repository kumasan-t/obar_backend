from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
db = SQLAlchemy()


class Purchase(db.Model):

    __tablename__ = 'purchase'

    purchase_number = db.Column(db.Integer(), primary_key=True)
    purchase_date = db.Column(db.Date())
    purchase_customer_mail_address = db.Column(db.String(), db.ForeignKey('customer.customer_mail_address'))
    purchase_item = db.relationship('PurchaseItem')

    def __repr__(self):
        return '<Purchase {}{} >'.format(self.purchase_number, self.purchase_customer_mail_address)


class Customer(db.Model):

    __tablename__ = 'customer'

    customer_mail_address = db.Column(db.String(), primary_key=True)
    customer_pin_hash = db.Column(db.String())  # has to be hashed
    customer_first_name = db.Column(db.String())
    customer_last_name = db.Column(db.String())
    purchase = db.relationship('Purchase', backref='Customer')

    def set_password(self, password):
        self.customer_pin_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Customer %r>' % self.customer_mail_address


# TODO: add description (or name) field
class Product(db.Model):

    __tablename__ = 'product'

    product_number = db.Column(db.Integer(), primary_key=True)
    product_availability = db.Column(db.Boolean())
    product_price = db.Column(db.Integer())
    product_unit = db.Column(db.Integer())
    product_discount = db.Column(db.Float(), default=0)
    purchaseItem = db.relationship('PurchaseItem', backref='Product')

    def __repr__(self):
        return '<Product {}>'.format(self.product_number)


class PurchaseItem(db.Model):
    __tablename__ = 'purchase_item'
    purchase_item_number = db.Column(db.Integer(), primary_key=True)
    purchase_item_quantity = db.Column(db.Integer())
    purchase_item_product_number = db.Column(db.Integer(), db.ForeignKey('product.product_number'))
    purchase_item_purchase_number = db.Column(db.Integer(), db.ForeignKey('purchase.purchase_number'))

    def __repr__(self):
        return '<PurchaseItem {}{}>'.format(self.purchase_item_number, self.purchase_purchase_item)
