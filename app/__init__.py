from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
import logging
from logging.handlers import RotatingFileHandler
import os
#from app.bin.stock_data_proc import update_stock_prices, populate_stock_prices_from_csv
from apscheduler.schedulers.background import BackgroundScheduler
import csv
import datetime
#from app.models import  StockPrice


"""
appliation setup - 
"""

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



def update_stock_prices():
    print(f'Scheduler runs update_stock_prices()')

    # Assuming your CSV files are stored in a directory
    csv_directory = os.path.join(os.getcwd(),'stock_data')
    # Loop through CSV files and update stock prices
    for csv_file in os.listdir(csv_directory):
        if csv_file.endswith('.csv'):
            csv_file_path = os.path.join(csv_directory, csv_file)
            populate_stock_prices_from_csv(csv_file_path)


def populate_stock_prices_from_csv(csv_file_path):
    print(f'Scheduler runs populate_stock_prices_from_csv()')
    with open(csv_file_path, 'r') as file:
        stock_id = os.path.basename(csv_file_path).replace('.csv','').replace('history','')
        reader = csv.reader(file)
        # Skip the header if present
        next(reader, None)
        for row in reader:
            # Assuming the CSV format is: date, stock_id, current_price, current_volume
            date_str, open, close, volume = row
            date = datetime.strptime(date_str, '%m/%d/%Y')
            # Create a StockPrice instance
            stock_price = StockPrice(
                stock_id=stock_id,
                date=date,
                current_price=float(close),
                current_volume=int(volume)
            )
            # Add the instance to the SQLAlchemy session
            db.session.add(stock_price)
print('*** initializing scheduler ***')
scheduler = BackgroundScheduler()
scheduler.add_job(update_stock_prices, 'interval', hours=1)
scheduler.start()


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
