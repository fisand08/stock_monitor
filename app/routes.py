from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PortfolioForm
from app.models import User, Portfolio, PortfolioStock
from app import Stock, StockPrice
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from functools import wraps
from flask import jsonify


"""
Logic executed before every request; executed before any view function
"""
"""
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc) # adding to db - no .add() needed here
        db.session.commit() # committing to db
"""
@app.route('/', methods=['GET', 'POST'])  # decorator for following function
@app.route('/index', methods=['GET', 'POST'])  # 2nd decorator
@login_required  # although it's index, we can set that here - not logged in person will be sent to login function
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
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data)) # query user from DB
        if user is None or not user.check_password(form.password.data): # password check
            flash('Invalid username or password') # flash field response if wrong password
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data) # username and pw are correct -> login
        """
        Adding some logic to bring user to page that he wanted to access before he got
        forced to login; request variable contains information of initial request
        """
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        
        return redirect(next_page)
    return render_template('login.html',title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')  # <> brackets allow dynamic URL like youtube.com/FarioStalking
@login_required # only accessible to logged-in users
def user(username):
    user = db.first_or_404(sa.select(User).where(User.username == username))
    alt_names = ['profil_' + x for x in ['guati','schatzi','schatzus','schatzo']]
    portfolios = ['NVS.SW,APPLE,DOWJON','ROG.SW,NVS.SW']
    return render_template('user.html', user=user, alt_names=alt_names, portfolios=portfolios)

@app.route('/error_404', methods=['GET', 'POST'])
def error_404():
    return render_template('404.html'), 404

@app.route('/error_403', methods=['GET', 'POST'])
def error_403():
    return render_template('403.html'), 403

@app.route('/error_500', methods=['GET', 'POST'])
def error_500():
    return render_template('500.html'), 500


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@app.route('/explore')
def explore():
    # Query for Stock objects
    stocks_query = db.session.query(Stock).all()[:20]
    # Query for StockPrice objects
    stock_prices_query = db.session.query(StockPrice).order_by(StockPrice.id.desc()).limit(10).all()
    # Portfolios
    portfolios_query = db.session.query(Portfolio).all()
    return render_template('explore.html', portfolios = portfolios_query, stocks=stocks_query, stock_prices=stock_prices_query)
# Update routes.py
@app.route('/manage_portfolio', methods=['GET', 'POST'])
@login_required
def manage_portfolio():
    form = PortfolioForm()
    stocks = Stock.query.all()
    stock_choices = [(stock.abbreviation, stock.full_name) for stock in stocks]

    portfolios = Portfolio.query.all()
    portfolio_choices = [(portfolio.id, portfolio.name) for portfolio in portfolios]

    form.stock.choices = stock_choices
    form.portfolios.choices = portfolio_choices

    current_stocks = {}

    # Set default selection to the first portfolio if no selection is made
    if not form.portfolios.data and portfolio_choices:
        default_portfolio_id = portfolio_choices[0][0]
        form.portfolios.data = default_portfolio_id
        selected_portfolio = Portfolio.query.get(default_portfolio_id)
        if selected_portfolio:
            for ps in selected_portfolio.stocks:
                current_stocks[ps.stock.full_name] = ps.amount

    if form.validate_on_submit():
        print(f"Form data: {form.data}")

    selected_portfolio_id = form.portfolios.data
    if selected_portfolio_id:
        selected_portfolio = Portfolio.query.get(selected_portfolio_id)
        stocks_in_portfolio = selected_portfolio.stocks
        for ps in stocks_in_portfolio:
            current_stocks[ps.stock.full_name] = ps.amount

    return render_template('manage_portfolio.html', form=form, current_stocks=current_stocks)

@app.route('/get_portfolio_data/<int:portfolio_id>', methods=['GET'])
@login_required
def get_portfolio_data(portfolio_id):
    portfolio = Portfolio.query.get(portfolio_id)
    if portfolio:
        current_stocks = {}
        for ps in portfolio.stocks:
            current_stocks[ps.stock.full_name] = ps.amount
        # Render the template with the updated data and return as string
        return render_template('current_stocks.html', current_stocks=current_stocks)
    return jsonify({'error': 'Portfolio not found'}), 404


"""
@app.route('/manage_portfolio', methods=['GET', 'POST'])
@login_required
def manage_portfolio():
    form = PortfolioForm()
    stocks = Stock.query.all()
    stock_choices = [(stock.abbreviation, stock.full_name) for stock in stocks]

    portfolios = Portfolio.query.all()
    portfolio_choices = [(portfolio.id, portfolio.name) for portfolio in portfolios]

    form.stock.choices = stock_choices
    form.portfolios.choices = portfolio_choices

    if form.validate_on_submit():
        print(f"Form data: {form.data}")

    current_stocks = {}

    selected_portfolio_id = form.portfolios.data
    if selected_portfolio_id:
        selected_portfolio = Portfolio.query.get(selected_portfolio_id)
        stocks_in_portfolio = selected_portfolio.stocks
        for ps in stocks_in_portfolio:
            current_stocks[ps.stock.full_name] = ps.amount

    print(f"Selected Portfolio ID: {selected_portfolio_id}")
    print(f"Current Stocks: {current_stocks}")

    return render_template('manage_portfolio.html', form=form, current_stocks=current_stocks)
"""


"""
@app.route('/manage_portfolio', methods=['GET', 'POST'])
@login_required
def manage_portfolio():
    form = PortfolioForm()
    stocks = Stock.query.all()
    stock_choices = [(stock.abbreviation, stock.full_name) for stock in stocks]

    portfolios = Portfolio.query.all()
    portfolio_choices = [(portfolio.id, portfolio.name) for portfolio in portfolios]

    form.stock.choices = stock_choices
    form.portfolios.choices = portfolio_choices

    current_stocks = {}
    if form.validate_on_submit():
        selected_portfolio_id = form.portfolios.data
        selected_portfolio = Portfolio.query.get(selected_portfolio_id)
        stocks_in_portfolio = selected_portfolio.stocks
        for ps in stocks_in_portfolio:
            current_stocks[ps.stock.full_name] = ps.amount

    return render_template('manage_portfolio.html', form=form, current_stocks=current_stocks)
"""

"""
/////////// ADMIN PANEL //////////////
"""
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return redirect(url_for('error_403'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin', methods=['GET'])
@admin_required
def admin_panel():
    users = User.query.all()
    return render_template('admin_panel.html', users=users)

@app.route('/admin/clear_table/<table_name>', methods=['POST'])
@admin_required
def clear_table(table_name):
    tables = {
        'stocks': Stock,
        'stock_prices': StockPrice,
        'portfolio_stocks': PortfolioStock,
        'portfolios': Portfolio
    }
    if table_name in tables:
        table = tables[table_name]
        table.query.delete()
        db.session.commit()
        flash(f'{table_name.capitalize()} table cleared successfully', 'success')
    else:
        flash('Table not found', 'error')
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/<int:user_id>/edit', methods=['POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    is_admin = request.form.get('is_admin') == 'on'
    user.is_admin = is_admin
    db.session.commit()
    flash('User privileges updated successfully', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin_panel'))