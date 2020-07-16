from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, MultipleFileField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app.models import User, Topic

class EmailFormMixin():
    email = StringField('Email', validators=[DataRequired(), Email()])

class LoginForm(FlaskForm, EmailFormMixin):
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('SIGN IN')

class ContactForm(FlaskForm, EmailFormMixin):
    name = StringField('Name', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class UpdateProfileForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    image = FileField('Change Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    knewbie_id = SubmitField('Request A Knewbie ID')
    submit = SubmitField('Save')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    newPassword = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Password', validators=[DataRequired(), Length(min=8), EqualTo('newPassword', message='Password does not match')])
    submit = SubmitField('Save')

class StringFormMixin():
    title = StringField('String', validators=[DataRequired()])

class CodeForm(FlaskForm, StringFormMixin):
    submit = SubmitField('View Progress Report')

class NameForm(FlaskForm, StringFormMixin): 
    submit = SubmitField('Create')

class JoinClassForm(FlaskForm, StringFormMixin):
    submit = SubmitField('Join Class')

class ChangeKnewbieForm(FlaskForm):
    submit = SubmitField('Request A New Knewbie ID')
