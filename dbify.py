from obar import create_app
from obar.models import db

db.create_all(app=create_app())

