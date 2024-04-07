from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)  # Apply configuration from config.py
db = SQLAlchemy(app) # line for DB
migrate = Migrate(app, db) # line for db migration

from app import routes
