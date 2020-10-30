from flask_script import Manager
from sqlalchemy import Column, String, Integer, create_engine
from flask_migrate import Migrate, MigrateCommand

from app.app import create_app
from models import db
from config import Config

app = create_app(Config)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
