from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, MultipleFileField, SelectField, FileField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length

from app.models import User, Topic


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

class StringFormMixin():
    title = StringField('String', validators=[DataRequired()])

class CodeForm(FlaskForm, StringFormMixin):
    submit = SubmitField('View Progress Report')

class NameForm(FlaskForm, StringFormMixin): 
    submit = SubmitField('Create')

class DeleteForm(FlaskForm):
    submit = SubmitField('Delete')