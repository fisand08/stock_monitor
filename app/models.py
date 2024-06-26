from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.bin import get_random_color # import of self-coded routine

"""
Definition of DB
    - Classes correspond to tables
"""

class User(UserMixin, db.Model):  # inherts from db.Model, the bas lass for all models in SQLAlhemy
    # also inhertis from UserMixin from flask-login covering the required functions is_authenticated, is_ative is_anonymus and get_id()
    """
    - Each field is assigned a type or type hint
    - mapped_column provides additional configuration; e.g. if it's unique or indexed
    - "unique" modified gives error if values is added twice to DB
    """
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,  unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)

    """
    Relationship to new class Portfolio "author" object; so.relationship() is model class that represents the other side of the relationship;
    the "back_populates" arguments reference the name of the relationship attribute on the other side
    """
    portfolios: so.WriteOnlyMapped['Portfolio'] = so.relationship(back_populates='author')

    """
    - password hash is used instead of password to not store them as plain text if DB is comprimised
    - optional typing allows empty or "None"
    - from werkzeug, password hashing and it's checking are added as methods
    """
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))


    def avatar(self,size):
        """
        Alternative to Gravatar
        Example:  https://ui-avatars.com/api/?name=Andre+Fischer&?background=0D8ABC&color=fff 
        Returns URL to avatar image
        """
        bg_color = get_random_color(self.username)
        return f'https://ui-avatars.com/api/?name={self.username[0]}+{self.username[1]}&?background={bg_color}&color=fff&?size={size}'
        


    def __repr__(self):
        """
        - Tells python how to print objets of this class (e.g. good for debugging)
        """
        return '<User {}>'.format(self.username)
    

@login.user_loader  # user loader is registered with decorator
def load_user(id):
    """
    - flask-login needs to know about the DB, user is loaded via id
    """
    return db.session.get(User, int(id)) # needs to be converted to int as string 


class Portfolio(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), index=True, unique=True)  # each portfolio has a name which is Optional
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))  # use Datetime to get Swiss time
    stock_list: so.Mapped[str] = so.mapped_column(sa.String(256))
    """
    Map to foreign key of "User" class
    """
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),  index=True)
    author: so.Mapped[User] = so.relationship(back_populates='portfolios')

    def __repr__(self):
        return '<Portfolio {}>'.format(self.stock_list)
    

"""
__DB Syntax__

* Fire up the DB (at least from CLI)
``` 
from app import app, db
from app.models import User, Portfolio
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

