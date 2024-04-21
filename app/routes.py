from app import app, db
from flask import render_template, flash, redirect, url_for, request
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostPortfolio, PortfolioForm
from app.models import User, Portfolio, PortfolioStock
from app import Stock, StockPrice
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from flask import request
from urllib.parse import urlsplit
from datetime import datetime, timezone

"""
Logic executed before every request; executed before any view function
"""

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.now(timezone.utc) # adding to db - no .add() needed here
        db.session.commit() # committing to db

@app.route('/', methods=['GET', 'POST'])  # decorator for following function
@app.route('/index', methods=['GET', 'POST'])  # 2nd decorator
@login_required  # although it's index, we can set that here - not logged in person will be sent to login function
def index():
    mock_user = {'username':'Rikarda'}
    alt_names = ['guati','schatzi','schatzus','schatzo']
    form = PostPortfolio()
    if form.validate_on_submit():  # forms always are POST requests
        portfolio = Portfolio(stock_list=form.portfolio.data, author=current_user)
        db.session.add(portfolio)
        db.session.commit()
        flash('Your portfolio is now stored in database!')
        return redirect(url_for('index')) # it's recommended to have a redirect at the end of a post request


    u = db.session.get(User, 1)
    query = u.portfolios.select()
    user_portfolios = db.session.scalars(query).all()
    options = ['portfolio1','portfolio2','portfolio3']


    portfolio_query = sa.select(Portfolio)
    """
    Instead of db.session.scalars() we can call db.paginate().items to prohibit overflow of one page
    and make the DB requests smaller; takes several arguments:
        page: the page number, starting from 1; per_page: the number of items per page
        error_out: an error flag. If True, when an out of range page is requested a 404 error will be 
        automatically returned to the client. If False, an empty list will be returned for out of range pages.
    """
    page = request.args.get('page', 1, type=int)
    portfolios = db.paginate(portfolio_query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=portfolios.next_num) \
        if portfolios.has_next else None
    prev_url = url_for('index', page=portfolios.prev_num) \
        if portfolios.has_prev else None

    return render_template('index.html',user=mock_user, alt_names=alt_names, 
                           portfolios=portfolios.items, form=form, 
                           next_url=next_url, prev_url=prev_url,options=options,user_portfolios=user_portfolios)

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

@app.route('/portfolio_manager')
def portfolio_manager():
    # Query for Stock objects
    stocks_query = db.session.query(Stock).all()
    # Query for StockPrice objects
    stock_prices_query = db.session.query(StockPrice).all()[:10]



    return render_template('portfolio_manager.html', stocks=stocks_query, stock_prices=stock_prices_query)



"""
@ app.route('/add_portfolio')
@login_required
def add_portfolio():

    form = PostPortfolio()
    if form.validate_on_submit():  # forms always are POST requests
        portfolio = Portfolio(stock_list=form.portfolio.data, author=current_user)
        db.session.add(portfolio)
        db.session.commit()
        flash('Your portfolio is now stored in database!')
        return redirect(url_for('index')) # it's recommended to have a redirect at the end of a post request


    return render_template('add_portfolio.html',
                           form=form, 
                           )
"""
@ app.route('/add_portfolio', methods=['GET', 'POST'])
@login_required
def add_portfolio():
    form = PortfolioForm()

    # Populate the portfolio field choices with existing portfolios
    portfolios = Portfolio.query.all()
    form.portfolio.choices = [(portfolio.id, portfolio.name) for portfolio in portfolios]

    # Populate the stock field choices with available stocks
    stocks = Stock.query.all()
    form.stock.choices = [(stock.abbreviation, stock.full_name) for stock in stocks]

    if form.validate_on_submit():
        portfolio_name = form.name.data
        stock_abbreviation = form.stock.data
        action = form.action.data
        amount = form.amount.data

        # Retrieve the selected portfolio
        selected_portfolio_id = form.portfolio.data
        selected_portfolio = None

        # If a portfolio is selected, get it from the database
        if selected_portfolio_id:
            selected_portfolio = Portfolio.query.get(selected_portfolio_id)

        # If no portfolio is selected, create a new one
        if not selected_portfolio and portfolio_name:
            selected_portfolio = Portfolio(name=portfolio_name)
            db.session.add(selected_portfolio)
            db.session.commit()

        if not selected_portfolio:
            flash("Please select a portfolio or enter a new portfolio name.")
            return redirect(url_for('add_portfolio'))

        # Update portfolio stock
        stock = Stock.query.filter_by(abbreviation=stock_abbreviation).first()

        if not stock:
            flash("Invalid stock selected.")
            return redirect(url_for('add_portfolio'))

        portfolio_stock = PortfolioStock.query.filter_by(portfolio_id=selected_portfolio.id, stock_id=stock.id).first()
        
        if portfolio_stock:
            if action == 'buy':
                portfolio_stock.amount += amount
            elif action == 'sell':
                portfolio_stock.amount -= amount
        else:
            portfolio_stock = PortfolioStock(portfolio_id=selected_portfolio.id, stock_id=stock.id, amount=amount)
            db.session.add(portfolio_stock)
        
        db.session.commit()
        flash("Portfolio updated successfully.")
        return redirect(url_for('add_portfolio'))

    return render_template('add_portfolio.html', form=form)

@ app.route('/old_index')
def old_index():

    mock_user = {'username':'Rikarda'}
    alt_names = ['guati','schatzi','schatzus','schatzo']
    form = PostPortfolio()
    if form.validate_on_submit():  # forms always are POST requests
        portfolio = Portfolio(stock_list=form.portfolio.data, author=current_user)
        db.session.add(portfolio)
        db.session.commit()
        flash('Your portfolio is now stored in database!')
        return redirect(url_for('index')) # it's recommended to have a redirect at the end of a post request

    portfolio_query = sa.select(Portfolio)
    """
    Instead of db.session.scalars() we can call db.paginate().items to prohibit overflow of one page
    and make the DB requests smaller; takes several arguments:
        page: the page number, starting from 1; per_page: the number of items per page
        error_out: an error flag. If True, when an out of range page is requested a 404 error will be 
        automatically returned to the client. If False, an empty list will be returned for out of range pages.
    """
    page = request.args.get('page', 1, type=int)
    portfolios = db.paginate(portfolio_query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
    next_url = url_for('index', page=portfolios.next_num) \
        if portfolios.has_next else None
    prev_url = url_for('index', page=portfolios.prev_num) \
        if portfolios.has_prev else None

    return render_template('old_index.html',user=mock_user, alt_names=alt_names, 
                           portfolios=portfolios.items, form=form, 
                           next_url=next_url, prev_url=prev_url)
    #return render_template('old_index.html')