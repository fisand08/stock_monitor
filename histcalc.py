from app import app, db
from app.models import Portfolio

# Create the Flask application
# Use the application context
with app.app_context():
    # Retrieve all existing portfolios
    existing_portfolios = Portfolio.query.all()

    # Loop through each portfolio and compute its history
    for portfolio in existing_portfolios:
        print(portfolio.name)
        portfolio.compute_portfolio_history()

    # Commit changes to the database
    db.session.commit()

