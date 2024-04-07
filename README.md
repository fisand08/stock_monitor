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
* __init__.py
* routes.py
* forms.py

## Getting Started

### Dependencies

* venv
* flask
* flask-wtf  (for forms)
* flask-sqlalchemy (for DB; supports SQLite, MySQL, and PostreSQL)
* flask-migrate (to migrate DB)
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
"set FLASK_APP=stocks.py
```

* Run app
```
flask run --reload
```