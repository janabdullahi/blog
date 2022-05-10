from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user 
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20), 
                                Regexp('^\w+$', message="Username must contain letters, numbers or underscore")])
    role = SelectField('Register As', choices=[(2, 'Blogger'), (3, 'Portal')])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                                Regexp(".*[a-z][A-Z][0-9][!@#\$&*~].* ", message="Password contains Lowercase"),
                                Regexp(".*[A-Z].*", message=" ,Uppercase"),
                                Regexp(".*[0-9].*", message=",Digits"),
                                Regexp(".*?[!@#\$&*~].*", message="and only one symbol at least")])

    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is already exist!.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(' Email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    password = PasswordField('password')
    new_password = PasswordField('New Password',validators=[DataRequired(),
                                Regexp(".*[a-z].*", message="password contains Lowercase"),
                                Regexp(".*[A-Z].*", message="password contains Dppercase"),
                                Regexp(".*[0-9].*", message="password contains Digit"),
                                Regexp(".*?[!@#\$&*~].*", message="password must contain only one symbol at least")])

    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')
    

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already exist. Please select different username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email is already exist. Please select different email.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),Length(min=2, max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('add a picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post') 
