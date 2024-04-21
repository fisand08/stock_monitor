import csv
import os
from datetime import datetime
from flask import current_app
from app.models import StockPrice

def populate_stock_prices_from_csv(csv_file_path):
    print(f'Scheduler runs populate_stock_prices_from_csv()')
    db = current_app.db  # Accessing db from the current application context
    update_stock_prices = current_app.update_stock_prices  # Accessing update_stock_prices from the current application context

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
    
    # Commit changes to the database after processing each CSV file
    db.session.commit()
    # After updating prices from all CSV files, trigger the main update_stock_prices function
    update_stock_prices()

    # Optional: Close the database session to free up resources
    db.session.close()
