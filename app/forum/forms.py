from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, MultipleFileField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

class PostForm(FlaskForm):
    content = TextAreaField('Say something', validators=[DataRequired()])
    submit = SubmitField('Post')

class ThreadForm(PostForm):
    title = StringField('Title', validators=[DataRequired()])

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')
