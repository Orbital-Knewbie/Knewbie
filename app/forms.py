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

class DeactivateForm(FlaskForm, EmailFormMixin):
    submit = SubmitField('DEACTIVATE')

class RegistrationForm(FlaskForm, EmailFormMixin):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ContactForm(FlaskForm, EmailFormMixin):
    name = StringField('Name', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')

class ResetPasswordForm(FlaskForm, EmailFormMixin):
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with the email you have entered. \
            Please ensure you have entered the correct email address or create a new account.')

class NewPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update Password')

class QuestionForm(FlaskForm):
    topic = SelectField('Select Topic', choices=[(0, 'Select Topic'), \
        *[(topic.id, topic.name) for topic in Topic.query.all()]], validators=[DataRequired()], coerce=int)
    qn = StringField('Input Question', validators=[DataRequired()])
    op1 = StringField('Option 1', validators=[DataRequired()])
    op2 = StringField('Option 2', validators=[DataRequired()])
    op3 = StringField('Option 3', validators=[DataRequired()])
    op4 = StringField('Option 4', validators=[DataRequired()])
    corrOp = SelectField('Correct Option', choices=[(0, 'Select Correct Option'), \
        (1, 'Option 1'), (2, 'Option 2'), (3, 'Option 3'), (4, 'Option 4')], validators=[DataRequired()], coerce=int)
    img = MultipleFileField('Attach Image')
    submit = SubmitField('Save and Add New Question')
    complete = SubmitField('Save and Complete Quiz')

class UpdateProfileForm(FlaskForm):
    firstName = StringField('First Name', validators=[DataRequired()])
    lastName = StringField('Last Name', validators=[DataRequired()])
    image = FileField('Change Image', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
    knewbie_id = SubmitField('Request A Knewbie ID')
    submit = SubmitField('Save')

#class UpdateAccountForm(FlaskForm):
#    firstName = StringField('First Name', validators=[DataRequired()])
#    lastName = StringField('Last Name', validators=[DataRequired()])
#    email = StringField('Email', validators=[DataRequired(), Email()])
#    password = PasswordField('Current Password', validators=[DataRequired()])
#    password1 = PasswordField('New Password', validators=[DataRequired()])
#    password2 = PasswordField(
#        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
#    submit = SubmitField('Save')

#    def validate_password(self, password_hash):
#        if not current_user.check_password(password):
#            user = User.query.filter_by(password_hash=password.data).first()
#            if user is not None:
#                raise ValidationError('You cannot reuse your old password. Please choose a different password.')

#    def validate_email(self, email):
#        if email.data == current_user.email:
#            user = User.query.filter_by(email=email.data).first()
#            if user is not None:
#                raise ValidationError('Email is the same as the registered email. Please use a different email address.')
#    submit = SubmitField('Create Question')

class PostForm(FlaskForm):
    content = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Post')

class ThreadForm(PostForm):
    title = StringField('Title', validators=[DataRequired()])

class StringFormMixin():
    title = StringField('String', validators=[DataRequired()])

class CodeForm(FlaskForm, StringFormMixin):
    submit = SubmitField('View Progress Report')

class NameForm(FlaskForm, StringFormMixin): 
    submit = SubmitField('Create')

class DeleteClassForm(FlaskForm, StringFormMixin):
    submit = SubmitField('Delete Class')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')

class JoinForm(FlaskForm, StringFormMixin):
    submit = SubmitField('Add to Class')

class JoinClassForm(FlaskForm, StringFormMixin):
    submit = SubmitField('Join Class')