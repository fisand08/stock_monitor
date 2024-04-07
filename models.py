from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):  # inherts from db.Model, the bas lass for all models in SQLAlhemy
    """
    - Each field is assigned a type or type hint
    - mapped_column provides additional configuration; e.g. if it's unique or indexed
    """
    
    id: so.Mapped[int] = so.mapped_column(primary_key = True)  # adds "id" as primay key
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    """
    - password hash is used instead of password to not store them as plain text if DB is comprimised
    - optional typing allows empty or "None"
    """
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    def __rep__(self):
        """
        - Tells python how to print objets of this class (e.g. good for debugging)
        """
        return '<User {}'.format(self.username)