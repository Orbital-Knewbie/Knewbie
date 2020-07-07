#from flask_login import current_user
from flask_wtf import FlaskForm
#from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, MultipleFileField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app.models import User, Topic


class EmailFormMixin():
    email = StringField('Email', validators=[DataRequired(), Email()])

class LoginForm(FlaskForm, EmailFormMixin):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('SIGN IN')

class RegistrationForm(FlaskForm, EmailFormMixin):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class DeactivateForm(FlaskForm, EmailFormMixin):
    submit = SubmitField('DEACTIVATE')

class ResetPasswordForm(FlaskForm, EmailFormMixin):
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with the email you have entered. \
            Please ensure you have entered the correct email address or create a new account.')

class NewPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')