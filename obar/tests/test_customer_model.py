import unittest
import os
from flask import Flask
from flask_testing import TestCase

from obar.models import db, Customer


class TestUserAuth(TestCase):
    TESTING = True

    def create_app(self):
        app = Flask(__name__)
        app.config['TESTING'] = self.TESTING
        # If unable to open the db file, check that the working directory is correct s.t. it must be the same of your
        # application: /path/to/application/obar_backend/
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.getcwd(), r'obar\obar_database.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        db.init_app(app)

        return app

    def setUp(self):
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_encode_auth_token(self):
        user = Customer(
            customer_mail_address='test@test.com',
            customer_pin_hash=str(12612),
            customer_first_name='foo',
            customer_last_name='bar'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, bytes))

    def test_decode_auth_token(self):
        user = Customer(
            customer_mail_address='test@test.com',
            customer_pin_hash=str(12612),
            customer_first_name='foo',
            customer_last_name='bar'
        )
        db.session.add(user)
        db.session.commit()
        auth_token = user.encode_auth_token()
        self.assertTrue(isinstance(auth_token, bytes))
        self.assertTrue(Customer.decode_auth_token(auth_token.decode("utf-8")) == user.customer_mail_address)


if __name__ == '__main__':
    unittest.main()
