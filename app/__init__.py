from flask import Flask
from config import Config

app = Flask(__name__)
app.config.from_object(Config)  # Apply configuration from config.py

from app import routes
