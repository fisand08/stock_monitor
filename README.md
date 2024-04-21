# Stock monitor

Interface to check a stock portfolio against stock data to check for profit/losses.

## Development:


1) unify css to one file
2) finish portfolio adder (looks and functionality) - e.g. it should just show the name field for entering a name if you add a new portfolio - it should now be able to access the data from the stocks table to display stocks to choose from
3) provide way to modify scrapers input
 ( first check if scraper dynamically checks his input.txt file to see if there is a new stock),
this will allow to add new stocks to the tool

* improve css and looks (e.g. yahoo portfolio manager)
* database
	* make sure stock prices are added from stocks csv files
	* general stock data read from general stock csv file
* portfolio manager
	* finish form, show (if not new) all stocks on the side
* modify index tab
* scraping manager: allow new stocks to be added, allow update (run scraper once, update database) with the click of a button
* admin panel


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