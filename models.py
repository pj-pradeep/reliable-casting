import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()

def setup_db(app):
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


def drop_db_and_create_new_db():
    db.drop_all()
    db_create_all()