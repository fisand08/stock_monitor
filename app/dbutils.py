import csv
import os
from datetime import datetime
from flask import current_app
from .models import StockPrice
from apscheduler.schedulers.background import BackgroundScheduler

def sensor():
    """ Function for test purposes. """
    print("Sensor function executed!")  # Debugging statement
    f_o = open('test.txt', 'w')
    f_o.write('test')
    f_o.close()
    return True

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sensor, 'interval', seconds=60)  # Run every 60 seconds
    scheduler.start()




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
			
