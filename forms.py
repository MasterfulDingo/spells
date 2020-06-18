from flask_wtf import FlaskForm
from wtforms import Form, StringField, TextField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class SpellSearchForm(Form):
    choices = [('level','level'),('school','school'),('range','range')]
    select = SelectField('Search for spells:', choices=choices)
    search = StringField('')