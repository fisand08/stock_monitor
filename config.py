import os
basedir = os.path.abspath(os.path.dirname(__file__)) # defines base dir of the app

class Config:
    # Secret key against Csrf
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    # e-Mail server details for error handling
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['andre_fischer1994@hotmail.com']