# Stock monitor

Interface to check a stock portfolio against stock data to check for profit/losses.

## Development:

* Urgent
	* Change portfolio manager:
		* make sure currently selected portfolio is displayed in table in right section
		* make two tabls within the page - one for modification, one for adding a new one (only changing left tab)
		* add a 3rd tab showing the current progression of the selected stock (plot) - give the plot some options

* General

	* modify index tab: make it lake yahoo
	* improve css and looks (e.g. yahoo portfolio manager)
	* Scraping manager
		* check if the scraper dynamically checks input_stocks.txt 
		* add functionality to portfolio manager to change this text file (also give some checking functionality visiting yahoo stocks if the provided code is valid)

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