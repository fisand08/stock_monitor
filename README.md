# Stock monitor

Interface to check a stock portfolio against stock data to check for profit/losses.

## Description

Currently in development along Flask tutorial from https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iii-web-forms

Tree:

* app
    * templates (HTML templates)
        * base.html (basis for default templates with header, flash messages etc. to inherit)
        * index.html (landing page)
        * login.html (login form)
* __init__.py (helps setting up the appliation)
* routes.py (used to start appliation)
* forms.py (place to put forms such as login)
* models.py (place to define DB models)

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