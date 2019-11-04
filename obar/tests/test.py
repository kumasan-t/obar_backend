import datetime
import unittest
from flask import Flask
from flask_testing import TestCase
from werkzeug.security import generate_password_hash
from obar.models import db, Customer, Product, Purchase, PurchaseItem

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.inspection import inspect
from sqlite3 import Connection as SQLite3Connection


class TestDatabase(TestCase):
    TESTING = True

    def create_app(self):

        app = Flask(__name__)
        app.config['TESTING'] = self.TESTING
        app.config['SQLALCHEMY_DATABASE_URI'] = r'sqlite:///D:\Documents\side_project\Flask-OBar\obar\tests\test.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        return app

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):

        db.session.remove()
        db.drop_all()

    def test_customer_insert_SQLAlchemy_session(self):
        """Tests Customer instance insertion
        Takes a dummy customer and inserts her in the db
        :return:
        """
        test_customer = get_dummy_customer()
        db.session.add(test_customer)
        db.session.commit()
        assert inspect(test_customer).persistent

    # Testing insertion on every table

    def test_purchase_insert_SQLAlchemy_session(self):
        """Tests Purchase instance insertion
        Takes a dummy customer and a dummy purchase and inserts them in the db.
        Customer instance is needed due to Foreign Key constraint on Purchase.
        :return:
        """
        test_customer = get_dummy_customer()
        test_purchase = get_dummy_purchase()

        db.session.add(test_customer)
        db.session.add(test_purchase)
        db.session.commit()
        assert inspect(test_purchase).persistent

    def test_product_insert_SQLAlchemy_session(self):
        """Tests Product insertion
        Takes a dummy Product and insert it in db
        :return:
        """
        test_product = get_dummy_product()
        db.session.add(test_product)
        db.session.commit()
        assert inspect(test_product).persistent

    def test_purchase_item_SQLAlachemy_session(self):
        """Tests Purchase Item insertion
        Takes a dummy Purchase Item and inserts it in db.
        Customer, Product and Purchase instances needed due to Foreign Key constraints
        :return:
        """
        test_product = get_dummy_product()
        test_purchase = get_dummy_purchase()
        test_purchase_item = get_dummy_purchase_item()
        test_customer = get_dummy_customer()

        db.session.add(test_product)
        db.session.add(test_customer)
        db.session.add(test_purchase)
        db.session.add(test_purchase_item)
        db.session.commit()
        assert inspect(test_purchase_item).persistent

    # Testing exception raise on every table containing a Foreign Key constraint

    def test_raise_exception_purchase_insert_SQLAlchemy_session(self):
        """Tests Exception raise of Purchase instance insertion without a referenced Foreign Key
        Takes a dummy purchase and inserts it in the db
        :return:
        """
        test_purchase = get_dummy_purchase()
        db.session.add(test_purchase)
        TestCase.assertRaises(self, IntegrityError, db.session.commit)

    def test_raise_exception_product_foreign_key_purchase_item_insert(self):
        """Tests Exception raise in  Purchase Item instance insertion
        Takes a dummy purchase item and inserts it in the db without any referenced Foreign Key on Product.
        the first of the two Foreign key
        :return:
        """
        test_purchase_item = get_dummy_purchase_item()
        test_purchase = get_dummy_purchase()
        test_customer = get_dummy_customer()
        db.session.add(test_customer)
        db.session.add(test_purchase)
        db.session.add(test_purchase_item)
        TestCase.assertRaises(self, IntegrityError, db.session.commit)

    def test_raise_exception_purchase_foreign_key_purchase_item_insert(self):
        """Tests Exception raise in Purchase Item instance insertion
        Takes a dummy purchase item and inserts it in the db without any referenced Foreign Key on Purchase.
        :return:
        """
        test_purchase_item = get_dummy_purchase_item()
        test_product = get_dummy_product()
        db.session.add(test_product)
        db.session.add(test_purchase_item)
        TestCase.assertRaises(self, IntegrityError, db.session.commit)

    # Testing table back-references from SQLAlchemy

    def test_customer_backref_SQLAlchemy_session(self):
        """Tests Customer back reference on Purchase table
        Takes the persistent instance of a customer and check if it correctly references a purchase through backref.
        :return:
        """
        test_customer = get_dummy_customer()
        test_purchase = get_dummy_purchase()
        db.session.add(test_customer)
        db.session.add(test_purchase)
        db.session.commit()
        assert test_purchase in test_customer.purchase


def get_dummy_customer():
    """
    Returns an instance of Customer for testing purposes
    :return: A Customer object
    """
    return Customer(customer_mail_address='test@test.com',
                    customer_pin=generate_password_hash(str(123456)),
                    customer_first_name='foo',
                    customer_last_name='bar')


def get_dummy_purchase():
    """
    Returns an instance of Purchase for testing purposes
    :return: a Purchase object
    """
    return Purchase(purchase_number=10002,
                    purchase_date=datetime.datetime.now(),
                    purchase_customer_mail_address='test@test.com')


def get_dummy_purchase_item():
    """
    Returns an instance of PurchaseItem for testing purposes
    :return: A PurchaseItem object
    """
    return PurchaseItem(purchase_item_number=10003,
                        purchase_item_quantity=10,
                        purchase_item_product_number=99999,
                        purchase_item_purchase_number=10002)


def get_dummy_product():
    """
    Returns an instance of Product for testing purposes
    :return: A Product object
    """
    return Product(product_number=99999,
                   product_availability=True,
                   product_price=500,
                   product_unit=900,
                   product_discount=0.00003)


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


if __name__ == '__main__':
    unittest.main()
