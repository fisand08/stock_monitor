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
        print(f'stocks: {self.stocks}')
        for portfolio_stock in self.stocks:
            print(f'stock_id: {portfolio_stock.stock_id}')
            stock_q = Stock.query.filter_by(id=portfolio_stock.stock_id).first()
            stock_abbrev = stock_q.abbreviation + '_'
            # print(f'stock_abbrev: {stock_q}')
            # print(f'stock_abbrev: {stock_abbrev}')
            print(f'date {date}')
            stock_price = StockPrice.query.filter_by(stock_id=stock_abbrev, date=date).first()
            if stock_price:
                # print(f'stok amount {portfolio_stock.amount} stock price {stock_price.current_price}')
                value += stock_price.current_price * portfolio_stock.amount
            else:
                print(f'no stock price found for {stock_abbrev} at date {date}')
                add = False
        if add:  # stock price was not found - only if calculation is proper, db will be updated
            existing_record = PortfolioHistory.query.filter_by(portfolio_id=self.id, timestamp=datetime.combine(date, datetime.min.time())).first()

            # existing_record = PortfolioHistory.query.filter_by(portfolio_id=self.id, timestamp=date).first()
            if existing_record:
                print('replacing value')
                existing_record.value = value  # Update the value
            else:
                print('record does not exist yet')
                # If no record exists, create a new one
                portfolio_history = PortfolioHistory(portfolio_id=self.id, timestamp=date, value=value)
                db.session.add(portfolio_history)

            print(f'portfolio {self.name} with id={self.id} has value {value} at date {date}')
            db.session.commit()
            return value


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


"""
def update_portfolio_history(portfolio):
    date = datetime.now().date()
    value = portfolio.calculate_portfolio_value(date)
    portfolio_history = PortfolioHistory(portfolio_id=portfolio.id, timestamp=datetime.now(), value=value)
    db.session.add(portfolio_history)
"""


"""
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

    def calculate_initial_price(self):
        initial_price = 0
        for portfolio_stock in self.stocks:
            latest_stock_price = db.session.query(StockPrice).filter_by(stock_id=portfolio_stock.stock_id).order_by(StockPrice.date.asc()).first()
            if latest_stock_price:
                initial_price += latest_stock_price.current_price * portfolio_stock.amount
        return initial_price

    def update_current_value(self):
        total_value = 0
        for portfolio_stock in self.stocks:
            latest_stock_price = db.session.query(StockPrice).filter_by(stock_id=portfolio_stock.stock_id).order_by(StockPrice.date.desc()).first()
            if latest_stock_price:
                total_value += latest_stock_price.current_price * portfolio_stock.amount
        self.current_value = total_value
        db.session.commit()

    def is_profitable(self):
        return self.current_value > self.initial_value

    def compute_portfolio_history(self):
        # Calculate portfolio value at different time points and store in PortfolioHistory table
        start_date = self.timestamp.date()
        end_date = datetime.utcnow().date()
        current_date = start_date
        while current_date <= end_date:
            total_value = 0
            for portfolio_stock in self.stocks:
                stock_price = db.session.query(StockPrice).filter_by(stock_id=portfolio_stock.stock_id, date=current_date).first()
                if stock_price:
                    total_value += stock_price.current_price * portfolio_stock.amount
            portfolio_history = PortfolioHistory(portfolio_id=self.id, timestamp=current_date, value=total_value)
            db.session.add(portfolio_history)
            current_date += timedelta(days=1)
        db.session.commit()

"""


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
from app.models import User, Portfolio, PortfolioStock
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
