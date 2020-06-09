from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField, MultipleFileField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('SIGN IN')

class RegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    #def validate_username(self, username):
    #    user = User.query.filter_by(username=username.data).first()
    #    if user is not None:
    #        raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with the email you have entered. Please ensure you have entered the correct email address or create a new account.')

class NewPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')

class CreateQnForm(FlaskForm):
    topic = SelectField('Select Topic', choices=[('nth', 'Select Topic'), ('Est', 'Estimation'), ('Geo', 'Geometry'), ('Model', 'Model')], validators=[DataRequired()])
    qn = StringField('Input Question', validators=[DataRequired()])
    op1 = StringField('Option 1', validators=[DataRequired()])
    op2 = StringField('Option 2', validators=[DataRequired()])
    op3 = StringField('Option 3', validators=[DataRequired()])
    op4 = StringField('Option 4', validators=[DataRequired()])
    corrOp = SelectField('Correct Option', choices=[('nth', 'Select Correct Option'), ('Op1', 'Option 1'), ('Op2', 'Option 2'), ('Op3', 'Option 3'), ('Op4', 'Option 4')], validators=[DataRequired()])
    img = MultipleFileField('Attach Image')
    submit = SubmitField('Create Question')

class UpdateProfileForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    image = FileField('Change Image')
    submit = SubmitField('Save')

class UpdateAccountForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Current Password', validators=[DataRequired()])
    password1 = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Save')

    def validate_password(self, password_hash):
        if not current_user.check_password(password):
            user = User.query.filter_by(password_hash=password.data).first()
            if user is not None:
                raise ValidationError('You cannot reuse your old password. Please choose a different password.')

    def validate_email(self, email):
        if email.data == current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Email is the same as the registered email. Please use a different email address.')