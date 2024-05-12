from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import relationship # noqa
from app import app, db, login, Stock, StockPrice # noqa
from datetime import datetime, timezone, timedelta # noqa
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.bin.helpers import get_random_color


"""
Definition of DB
    - Classes correspond to tables
"""


class User(UserMixin, db.Model):  # inherts from db.Model, the bas lass for all models in SQLAlhemy
    # also inhertis from UserMixin from flask-login covering the required functions is_authenticated, is_ative is_anonymus and get_id()

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    portfolios: so.WriteOnlyMapped['Portfolio'] = so.relationship(back_populates='author', cascade='all, delete-orphan', passive_deletes=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    is_admin = db.Column(db.Boolean, default=False)  # New field for admin status

    def avatar(self, size):
        bg_color = get_random_color(self.username)
        return f'https://ui-avatars.com/api/?name={self.username[0]}+{self.username[1]}&?background={bg_color}&color=fff&?size={size}'

    def __repr__(self):
        return '<User {}>'.format(self.username)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


class Portfolio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True, nullable=False)
    author = db.relationship('User', back_populates='portfolios')
    current_value = db.Column(db.Float, default=0)
    initial_value = db.Column(db.Float, default=0)
    stocks = db.relationship('PortfolioStock', back_populates='portfolio', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Portfolio {self.name}>'

    def calculate_portfolio_value(self, date):
        value = 0
        add = True  # boolean to record if stock price was found

        # Retrieve the portfolio composition using the provided function
        print(f'Computing history of portfolio "{self.name}" with id "{self.id}" at {date}')
        portfolio_composition = calculate_portfolio_composition(self.id, date)
        print(portfolio_composition)
        # Iterate over portfolio composition to calculate portfolio value
        for stock_id, amount in portfolio_composition:
            stock_q = Stock.query.get(stock_id)
            if not stock_q:
                print(f'Stock with ID {stock_id} not found.')
                continue

            stock_abbrev = stock_q.abbreviation + '_'
            stock_price = StockPrice.query.filter_by(stock_id=stock_abbrev, date=date).first()

            if stock_price:
                value += stock_price.current_price * amount
            else:
                print(f'No stock price found for {stock_abbrev} at date {date}')
                add = False

        if add:
            existing_record = PortfolioHistory.query.filter_by(portfolio_id=self.id, timestamp=datetime.combine(date, datetime.min.time())).first()

            if existing_record:
                existing_record.value = value
            else:
                portfolio_history = PortfolioHistory(portfolio_id=self.id, timestamp=date, value=value)
                db.session.add(portfolio_history)

            print(f'Portfolio {self.name} with id={self.id} has value {value} at date {date}')
            db.session.commit()
            return value


# Maybe add in separate file later
from collections import defaultdict  # noqa


def calculate_portfolio_composition(portfolio_id, date):
    # Retrieve transactions for the given portfolio before or on the given date
    transactions = Transaction.query.filter_by(portfolio_id=portfolio_id).filter(Transaction.timestamp <= date).all()

    # Initialize a dictionary to store the holdings of each stock
    stock_holdings = defaultdict(int)

    # Process transactions to update holdings
    for transaction in transactions:
        if transaction.action == 'buy':
            stock_holdings[transaction.stock_id] += transaction.amount
        elif transaction.action == 'sell':
            stock_holdings[transaction.stock_id] -= transaction.amount

    # Convert stock holdings to a list of tuples for easier handling
    portfolio_composition = [(stock_id, amount) for stock_id, amount in stock_holdings.items()]

    return portfolio_composition


class PortfolioStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    amount = db.Column(db.Integer, default=0)

    portfolio = db.relationship('Portfolio', back_populates='stocks')
    stock = db.relationship('Stock')

    def __repr__(self):
        return f"PortfolioStock(Portfolio ID: {self.portfolio_id}, Stock ID: {self.stock_id}, Amount: {self.amount})"


class PortfolioHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<PortfolioHistory Portfolio ID: {self.portfolio_id}, Timestamp: {self.timestamp}, Value: {self.value}>'


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('portfolio.id'), nullable=False)
    stock_id = db.Column(db.Integer, db.ForeignKey('stock.id'), nullable=False)
    stock = db.relationship('Stock', foreign_keys=[stock_id], backref='transactions')
    action = db.Column(db.String(50), nullable=False)  # e.g., 'BUY', 'SELL'
    amount = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.now(timezone.utc))
    investment = db.Column(db.Float)

    def compute_investment(self):
        print(f'*************investment: id {self.id}  stock_id {self.stock_id} stock {self.stock}')
        stock_price = StockPrice.query.filter_by(stock_id=self.stock.abbreviation + '_').order_by(StockPrice.date.desc()).first()
        if self.action == 'buy':
            self.investment = -1 * stock_price.current_price * self.amount
        elif self.action == 'sell':
            self.investment = 1 * stock_price.current_price * self.amount
        else:
            print('error: action must be buy or sell')

    def __repr__(self):
        return f'<Transaction {self.action}: Stock {self.stock_id}, Amount {self.amount}, Timestamp {self.timestamp}>'


"""
__DB Syntax__

* Fire up the DB (at least from CLI)
```
from app import app, db
from app.models import User, Portfolio, PortfolioStock, PortfolioHistory
from app import Stock, StockPrice
import sqlalchemy as sa
```

* Adding entry to User table (only after commit changes are made to the DB)
```
u = User(username='susan', email='susan@example.com')
db.session.add(u)
db.session.commit()
```

* Simple query to a Table (in reverse alphabetical order)
```
query = sa.select(User).order_by(User.username.desc())
users = db.session.scalers(query).all()
print(users)
```

* Conditioned query
```
query = sa.select(User).where(User.username.like('s%'))
s_users = db.session.scalars(query).all()
print(s_users)
```

* Linked query (all portfolios by one user)
```
u = db.session.get(User, 1)
query = u.posts.select()
posts = db.session.scalars(query).all()
print(posts)
```

* Adding a portfolio

```
from app import app, db
from app.models import User, Portfolio, PortfolioStock, PortfolioHistory, Transaction
from app import Stock, StockPrice
import sqlalchemy as sa

with app.app_context():
    user_instance = User.query.first()
    stock_instance_1 = Stock.query.filter_by(id=5).first()
    stock_instance_2 = Stock.query.filter_by(id=3).first()
    quantity_1 = 15
    quantity_2 = 250
    portfolio = Portfolio(name="some_other_name2", author=user_instance,
        stocks=[PortfolioStock(stock=stock_instance_1, amount=quantity_1),
        PortfolioStock(stock=stock_instance_2, amount=quantity_2) ] )
    db.session.add(portfolio)
    db.session.commit()
```

"""


"""
example for association table - does not need "class" as it only contains foreign keys from other tables

followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
              primary_key=True)
)
"""
