from flask_wtf import FlaskForm
from wtforms import PasswordField,SubmitField,validators,TextField
from wtforms.fields.html5 import EmailField
class RegistrationForm(FlaskForm):
    first_name = TextField('first_name',validators=[validators.DataRequired()])
    last_name = TextField('last_name',validators=[validators.DataRequired()])
    email = EmailField('email',validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('password',validators=[validators.DataRequired(),validators.Length(min=8, message="Please choose a password of at least 8 characters")])
    password2 = PasswordField('password2',validators=[validators.DataRequired(),validators.EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Submit', [validators.DataRequired()])
class LoginForm(FlaskForm):
    loginemail = EmailField('email',validators=[validators.DataRequired(), validators.Email()])
    loginpassword = PasswordField('password',validators=[validators.DataRequired(message="Password field is required")])
    submit = SubmitField('Submit', [validators.DataRequired()])