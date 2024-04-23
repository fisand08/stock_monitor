from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
#from .dbutils import populate_stock_prices_from_csv


"""
SCHEDULER
"""
def sensor():
    """ Function for test purposes. """
    print("Sensor function executed!")  # Debugging statement
    f_o = open('test.txt', 'w')
    f_o.write('test')
    f_o.close()
    return True

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor,'interval',minutes=60)
# run all jobs now
for job in sched.get_jobs():
    job.modify(next_run_time=datetime.now())
sched.start()

"""
MAIN APP SETUP
"""
setup_scheduler()

app = Flask(__name__) # creates appliation instane
app.config.from_object(Config)  # Apply configuration from config.py
db = SQLAlchemy(app) # line for DB
migrate = Migrate(app, db) # line for db migration
login = LoginManager(app) # initializiation of flask-login
moment = Moment(app) # initialization of flask-moment
"""
The following statement tells flask which view function is used to login (name of the funtion)
Like that, pages can be restrited to logged-in users with the @login_required decorator
"""
login.login_view = 'login'

"""
Scheduler for automated update of stock data from csv when server is running
"""



if not app.debug:
    
    # Place where email logging might sit #

    """
    error logging
    """
    if not os.path.exists('logs'):
        os.mkdir('logs')
    """
    backupCount: last n log files are kept; maxBytes: maximal size of the log file
    """
    file_handler = RotatingFileHandler('logs/applog.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('App startup')

from app import routes, models, errors
