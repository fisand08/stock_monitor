from app import app, db
from flask import render_template, flash, redirect
from app.forms import LoginForm
from app.models import User
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user
from flask import request
from urllib.parse import urlsplit

@app.route('/')  # decorator for following function
@app.route('/index')  # 2nd decorator
def index():
    mock_user = {'username':'Rikarda'}
    alt_names = ['guati','schatzi','schatzus','schatzo']
    return render_template('index.html',user=mock_user, alt_names=alt_names)
    #return render_template('index.html',title='Starting page',user=mock_user)

@app.route('/login', methods=['GET','POST'])  # view function accepts "methods" (POST: browser to webserver)
def login():
    if current_user.is_authenticated:
        """
        User is sent back to index if already logged-in
        """
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username)) # query user from DB
        if user is None or not user.check_password(form.password.data): # password check
            flash('Invalid username or password') # flash field response if wrong password
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # username and pw are correct -> login
        """
        Adding some logic to bring user to page that he wanted to access before he got
        forced to login; request variable contains information of initial request
        """
        next_page = request.arg.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    return render_template('login.html',title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))