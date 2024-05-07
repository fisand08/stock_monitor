
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy as sa # noqa
import sqlalchemy.orm as so # noqa
# from sqlalchemy.orm import relationship
import csv
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy import func


"""
MAIN APP SETUP
"""
app = Flask(__name__)  # creates appliation instane
app.config.from_object(Config)  # Apply configuration from config.py
db = SQLAlchemy(app)  # line for DB
migrate = Migrate(app, db)  # line for db migration
login = LoginManager(app)  # initializiation of flask-login
moment = Moment(app)  # initialization of flask-moment
"""
The following statement tells flask which view function is used to login (name of the funtion)
Like that, pages can be restrited to logged-in users with the @login_required decorator
"""
login.login_view = 'login'


"""
DB model here to avoid circular import problem
"""


class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(10), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    market = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    prices = db.relationship('StockPrice', back_populates='stock')

    def __repr__(self):
        return f"Stock(abbreviation: {self.abbreviation}, full_name: {self.full_name})"


class StockPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    current_volume = db.Column(db.Integer, nullable=False)

    stock = db.relationship('Stock', back_populates='prices')

    def __repr__(self):
        return f"StockPrice(Stock ID: {self.stock_id}, Date: {self.date}, Price: {self.current_price}, Volume: {self.current_volume})"


"""
SCHEDULER AND RELATED FUNCTIONS
"""


def sensor():
    """ Function for test purposes. """
    print("Sensor function executed!")  # Debugging statement
    f_o = open('test.txt', 'w')
    f_o.write('test')
    f_o.close()
    return True


def update_stock_prices():
    task = 'stock prices'
    print(f'*** Scheduler: Starting update cylce of: "{task}" ***')
    # Assuming your CSV files are stored in a directory
    csv_directory = os.path.join(os.getcwd(), 'stock_data')
    # Loop through CSV files and update stock prices
    for csv_file in os.listdir(csv_directory):
        if csv_file.endswith('.csv'):
            csv_file_path = os.path.join(csv_directory, csv_file)
            populate_stock_prices_from_csv_efficient(csv_file_path)
    print(f'*** Scheduler: Finished update cylce of: {task} ***')


def populate_stock_prices_from_csv_efficient(csv_file_path):
    print(f'Scheduler: processing {os.path.basename(csv_file_path)}...')
    with app.app_context():  # Create an application context
        with open(csv_file_path, 'r') as file:
            stock_id = os.path.basename(csv_file_path).replace('.csv', '').replace('history', '')

            # Query to get the latest update date for the stock
            latest_update_date = db.session.query(func.max(StockPrice.date)).filter_by(stock_id=stock_id).scalar()

            reader = csv.reader(file)
            # Skip the header if present
            next(reader, None)
            stock_prices = []

            for row in reader:
                # Assuming the CSV format is: date, opening_price, closing_price, volume
                date_str, opening_price, closing_price, volume = row
                try:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()  # Parse as datetime.date object
                except Exception as e:  # flake8: noqa
                    print(e)
                    date = datetime.strptime(date_str, '%m/%d/%Y').date()  # Parse as datetime.date object

                # Skip entries before the latest update date
                if latest_update_date and date <= latest_update_date:
                    continue

                # Check if the entry already exists in the database
                existing_entry = StockPrice.query.filter_by(stock_id=stock_id, date=date).first()
                existing_entry_alt = StockPrice.query.filter_by(stock_id=stock_id + '_', date=date).first()
                if existing_entry or existing_entry_alt:
                    continue  # Skip insertion if the entry already exists

                # Create a StockPrice instance
                stock_price = StockPrice(
                    stock_id=stock_id,
                    date=date,
                    current_price=float(closing_price),
                    current_volume=int(volume)
                )
                # Add the instance to the list
                stock_prices.append(stock_price)

            # Add all the instances to the SQLAlchemy session in a single operation
            if stock_prices:
                print('*** Scheduler: updating {stock_id}***')
                db.session.add_all(stock_prices)
                db.session.commit()
            else:
                print('*** Scheduler: no new data found ***')


def call_overview_update():
    task = 'stock table'
    print(f'*** Scheduler: Starting update cylce of: "{task}" ***')
    csv_file_path = os.path.join(os.getcwd(), 'stocks_db.csv')
    populate_stock_overview(csv_file_path)
    print(f'*** Scheduler: Finished update cylce of: "{task}" ***')


def populate_stock_overview(csv_file_path):
    with app.app_context():
        with open(csv_file_path, 'r') as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:  # STOCK_ID	STOCK_NAME	MARKET	CURRENCY
                stock_id, stock_name, market, currency = row

                # Check if the entry already exists in the database
                existing_entry = Stock.query.filter_by(abbreviation=stock_id).first()

                if existing_entry:
                    print(f"Entry for stock_id: {stock_id} already exists. Skipping insertion.")
                    continue  # Skip insertion if the entry already exists

                stock = Stock(
                    abbreviation=stock_id,
                    full_name=stock_name,
                    market=market,
                    currency=currency
                )
                db.session.add(stock)
        db.session.commit()


"""
    id = db.Column(db.Integer, primary_key=True)
    abbreviation = db.Column(db.String(10), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    market = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(10), nullable=False)
    # Add more attributes as needed
    prices = relationship("StockPrice", back_populates="stock")
"""

sched = BackgroundScheduler(daemon=True)
sched.add_job(sensor, 'interval', minutes=60, start_date=datetime.now())
sched.add_job(update_stock_prices, 'interval', minutes=60, start_date=datetime.now())
sched.add_job(call_overview_update, 'interval', minutes=60, start_date=datetime.now())
# run all jobs now
"""
for job in sched.get_jobs():
    job.modify(next_run_time=datetime.now())
"""

sched.start()


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

from app import routes, models, errors  # noqa

"""

@app.teardown_appcontext
sched.shutdown()
"""
