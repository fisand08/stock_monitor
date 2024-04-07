from app import app
from flask import render_template, flash, redirect
from app.forms import LoginForm

@app.route('/')  # decorator for following function
@app.route('/index')  # 2nd decorator
def index():
    mock_user = {'username':'Rikarda'}
    alt_names = ['guati','schatzi','schatzus','schatzo']
    return render_template('index.html',user=mock_user, alt_names=alt_names)
    #return render_template('index.html',title='Starting page',user=mock_user)

@app.route('/login', methods=['GET','POST'])  # view function accepts "methods" (POST: browser to webserver)
def login():
    form = LoginForm()
    if form.validate_on_submit(): # eturns True if validators are ok
        # flash to show message to the user
        flash('Login requested for user {}, remember_me {}'.format(form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html',title='Sign in', form=form)