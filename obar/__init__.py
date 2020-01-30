import os
import logging
from obar.models import db
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_restplus import Api
from flask.logging import default_handler
from sqlalchemy import event
from sqlite3 import Connection as SQLite3Connection
from obar.apis import customer_namespace, product_namespace, purchase_namespace, \
    operation_namespace, auth_namespace, site_namespace


migrate = Migrate()
basedir = os.getcwd()


def create_app(test_config=None):
    app = Flask(__name__)
    app.logger.info('Current working directory: %s', basedir)
    srcdir = os.path.join(basedir, 'persistent')

    app.config.from_mapping(
        SECRET_KEY='developing',
        SQLALCHEMY_DATABASE_URI='sqlite:///' + os.path.join(srcdir,'obar_database.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    app.logger.addHandler(default_handler)
    logging.getLogger('sqlalchemy').addHandler(default_handler)

    # Adds an event listener for db connection.
    # Allows to execute the PRAGMA foreign_keys=ON; instruction in order
    # to enable the foreign key constraint check SQLite3
    from sqlalchemy.engine import Engine

    @event.listens_for(Engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        app.logger.info('Setting PRAGMA foreign_keys=ON;')
        if isinstance(dbapi_connection, SQLite3Connection):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

    # Import models to allow SQLAlchemy to create tables
    from obar.models import Customer, Purchase, PurchaseItem, Product, ProductImage, BlacklistToken, Site

    CORS(app)
    db.init_app(app)
    app.logger.info('Initialized database plug-in')

    migrate.init_app(app, db)
    app.logger.info('Initialized migration plug-in')

    api = Api(
        title='OBar',
        version='1.0',
        description='API documentation for OBar web-application <style>.models {display: none !important}</style>',
        # All API metadatas
    )

    api.add_namespace(customer_namespace.customer_ns)
    api.add_namespace(product_namespace.product_ns)
    api.add_namespace(purchase_namespace.purchase_ns)
    api.add_namespace(site_namespace.site_ns)
    api.add_namespace(operation_namespace.operation_ns)
    api.add_namespace(auth_namespace.auth_ns)
    api.init_app(app)
    # Ensure the instance folder exists, otherwise create it.
    try:
        os.makedirs(app.instance_path)
    except OSError:
        app.logger.info("Unable to create a new directory in %s: the directory may already exists.", app.instance_path)

    @app.route('/')
    def hello():
        return 'hello there!'

    return app




