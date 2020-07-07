from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, MultipleFileField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app.models import User, Topic


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

class QuizClassForm(FlaskForm):
    submit = SubmitField('Add Quiz to Class')

class EditNameForm(FlaskForm, StringFormMixin):
    submit = SubmitField('Edit Name')

class UpdateCodeForm(FlaskForm):
    submit = SubmitField('Change Class Code')