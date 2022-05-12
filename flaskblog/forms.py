from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user 
from wtforms import StringField, PasswordField, SubmitField, BooleanField,SelectField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError,Regexp
from flaskblog.models import User
from flask_ckeditor import CKEditorField


class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20), 
                                Regexp('^\w+$', message="Username Must Contain Letters, Numbers Or Underscore")])
    role = SelectField('Register As', choices=[(2, 'Blogger'), (3, 'Portal')])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Create New Password', validators=[DataRequired(),
                                Regexp(".*[a-z].*",message="Password Must Contain Lowercase"),
                                Regexp(".*[A-Z].*", message=" ,Uppercase"),
                                Regexp(".*[0-9].*", message=",Digits"),
                                Regexp(".*?[!@#\$&*~].*", message="And Only One Aymbol Atleast")])

    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username Is Already Exist!.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError(' Email Is Taken. Please Choose A Different One.')


class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    picture = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'png'])])
    password = PasswordField('password')
    new_password = PasswordField('Create new Password',validators=[DataRequired(),
                                Regexp(".*[a-z].*",message="Password Must Contain Lowercase"),
                                Regexp(".*[A-Z].*", message=" ,Uppercase"),
                                Regexp(".*[0-9].*", message=",Digits"),
                                Regexp(".*?[!@#\$&*~].*", message="And Only One Symbol Atleast")])
    confirm_password = PasswordField('Confirm Password', validators=[
                                EqualTo('new_password', message="Confirm Password Must Be Equal To New Password")])
    submit = SubmitField('Update')
    

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username Is Already Exist. Please Select Different Username.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email Is Already Exist. Please Select Different Email.')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(),Length(min=2, max=100)])
    #content = TextAreaField('Content', validators=[DataRequired()])
    content = CKEditorField('Content',validators=[DataRequired()]) 
    short_description = StringField('Short Description', validators=[DataRequired(),Length(min=50, max=200)])
    picture = FileField('Upload Photo', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post') 

class SearchForm(FlaskForm):
    searched = StringField('Searched',validators=[DataRequired()] )
    submit = SubmitField('Submit')