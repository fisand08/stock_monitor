# Stock monitor

Interface to check a stock portfolio against stock data to check for profit/losses.

## Development:

* next:

	* add way to display profitability of a portfolio (initial vs latest dat in portfoliohistory)
		-> can be done in the portfolio value computation - based on transaction history, a function like "calculate_portfolio_composition" can be used to get the actual composition of the portfolio -> the value claulation has to consider that.
		-> then, the prtofitbility can be simply computed with value and investments

	* display current price of stock when buying
	* allow user to specify amount of money to spend in a stock instead of just number - or at least display the amount before buying
	* fix currency issues (maybe while scraping)
	* scrape newest data and check if it works
	* then: index tab (recent investments, profitability, courses, ...)

* later:

	* add little table with genral stock details like dividend
	* Start working in index tab
		* portfolio contents, protitability (incl how much), graph
	* make flash message not appear on whole width
	* improve css and looks (e.g. yahoo portfolio manager)
	* Define internal currency

	
## Description

Currently in development along Flask tutorial from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

Tree:

* app
	* templates
		* 404.html
		* 500.html
		* bootstrap_wtf.html
		* edit_profil.html
		* index.html
		* login.html
		* register.html
		* user.html
	* static
		* img
			* dsmf_dots.png
			* loading.gif
		
	* __init__.py
	* bin.py
	* errors.py
	* forms.py
	* models.py
	* routes.py
config.py
stocks.py


## Getting Started

### Dependencies

* venv
* flask
* flask-wtf  (for forms)
* flask-sqlalchemy (for DB; supports SQLite, MySQL, and PostreSQL)
* flask-migrate (to migrate DB)
* flask-login (login management)
* flask-moment (timezone management)

### Executing program

* Run Anacoda console

* Create env (only first time)
```
python -m venv venv
```

* Activate env
```
cd venv
cd Scripts
activate
```

* Set ENV variable
```
set FLASK_APP=stocks.py  (export in Linux)
```

* Run app
```
flask run --reload
```

## Notes

### Database Migrations (Commits)

* To allow database migrations, flask-migrate was installed. Initially, "flask db init" is used as initialization of the migration directory". If changes to the DB model have been done, they can be commited similar to "git" like:
```
flask db migrate -m "your comment"
```
And then to make the database upgrade:
```
flask db upgrade
```

### Command line checking

* Use flask shell to avoid importing your app and DB models
```
flask shell
```

### Activate debugger

* During development, debugging mode can be activated by:
```
set FLASK_DEBUG=1   (export in Linux)
```