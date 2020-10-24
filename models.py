import os
from sqlalchemy import Column, String, Integer
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

class Actors(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String, nullable=False)

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'age': self.age
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
