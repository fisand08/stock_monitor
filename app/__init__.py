from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


"""
appliation setup - 
"""

app = Flask(__name__) # creates appliation instane
app.config.from_object(Config)  # Apply configuration from config.py
db = SQLAlchemy(app) # line for DB
migrate = Migrate(app, db) # line for db migration
login = LoginManager(app) # initializiation of flask-login
"""
The following statement tells flask which view function is used to login (name of the funtion)
Like that, pages can be restrited to logged-in users with the @login_required decorator
"""
login.login_view = 'login' 

from app import routes, models, errors
