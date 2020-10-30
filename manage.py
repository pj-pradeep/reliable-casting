from flask_script import Manager
from sqlalchemy import Column, String, Integer, create_engine
from flask_migrate import Migrate, MigrateCommand
from dotenv import load_dotenv

from app.app import create_app
from models import db
from config import Config

load_dotenv()
app = create_app(Config)

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
    