import os

class Config:
    # Secret key against Csrf
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
