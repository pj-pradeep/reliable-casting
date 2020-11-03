import os
from sqlalchemy import (
    Column, String, Integer, Date
)
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def setup_db(app):
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)


def drop_db_and_create_new_db():
    db.drop_all()
    db.create_all()


actor_movie = db.Table(
    'actor_movie',
    Column('actor_id', db.Integer, db.ForeignKey(
        'actors.id'), primary_key=True),
    Column('movie_id', db.Integer, db.ForeignKey(
        'movies.id'), primary_key=True)
)


class Actor(db.Model):
    __tablename__ = 'actors'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    movies = db.relationship(
        'Movie', secondary=actor_movie,
        backref=db.backref('movies', lazy=True))

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'gender': self.gender,
            'date_of_birth': self.date_of_birth
        }

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()


class Movie(db.Model):
    __tablename__ = 'movies'

    id = Column(Integer, primary_key=True)
    title = Column(String(120), unique=True, nullable=False)
    release_date = Column(Date, nullable=False)

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }
