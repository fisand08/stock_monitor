from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, RadioField,  PasswordField, BooleanField, SubmitField, TextAreaField, StringField
from wtforms.validators import InputRequired, ValidationError, DataRequired, Email, EqualTo, Length
import sqlalchemy as sa
from app import db
from app.models import User


class LoginForm(FlaskForm):
    """
    Class for login forms based on WTForms. 
    Validator DataRequired specified that field is not submitted empty
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    """
    Form for registering new user
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    """
    Checks if user and email are already registrered in DB
    wTForms automatically detects validation functions if "validate_<field_name>"
    """
    def validate_username(self, username):
        user = db.session.scalar(sa.select(User).where(
            User.username == username.data))
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == self.username.data))
            if user is not None:
                raise ValidationError('Please use a different username.')
        

class PortfolioForm(FlaskForm):
    portfolios = SelectField('Select Portfolio', choices=[])
    stock = SelectField('Select Stock', choices=[])
    amount = IntegerField('Amount', validators=[InputRequired()])
    action = RadioField('Action', choices=[('buy', 'Buy'), ('sell', 'Sell')], validators=[InputRequired()])
    submit = SubmitField('Submit')
