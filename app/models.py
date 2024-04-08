from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from datetime import datetime, timezone, timedelta

"""
Definition of DB
    - Classes correspond to tables
"""

class User(db.Model):  # inherts from db.Model, the bas lass for all models in SQLAlhemy
    """
    - Each field is assigned a type or type hint
    - mapped_column provides additional configuration; e.g. if it's unique or indexed
    """
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,  unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    #gender: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    """
    - password hash is used instead of password to not store them as plain text if DB is comprimised
    - optional typing allows empty or "None"
    """
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    """
    Relationship to new class Portfolio "author" object; so.relationship() is model class that represents the other side of the relationship;
    the "back_populates" arguments reference the name of the relationship attribute on the other side
    """
    posts: so.WriteOnlyMapped['Portfolio'] = so.relationship(back_populates='author')

    def __repr__(self):
        """
        - Tells python how to print objets of this class (e.g. good for debugging)
        """
        return '<User {}>'.format(self.username)
    

class Portfolio(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256), index=True, unique=True)  # each portfolio has a name which is Optional
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))  # use Datetime to get Swiss time
    stock_list: so.Mapped[str] = so.mapped_column(sa.String(256))
    """
    Map to foreign key of "User" class
    """
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id),  index=True)
    author: so.Mapped[User] = so.relationship(back_populates='posts')

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