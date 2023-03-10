from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, URL
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField, FileRequired,FileAllowed


##WTForm
class CreateEventForm(FlaskForm):
    title = StringField("Project Title", validators=[DataRequired()])
    ay = StringField("Academic Year", validators=[DataRequired()])
    group1 = StringField("Group Members", validators=[DataRequired()])
    group2 = StringField("Group Members", validators=[DataRequired()])
    group3 = StringField("Group Members", validators=[DataRequired()])
    guide = StringField("Project Guide", validators=[DataRequired()])
    img_url = StringField("Project Image URL" )
    submit = SubmitField("Create")

class RegisterForm(FlaskForm):
    name = StringField("Your Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class CommentForm(FlaskForm):
    comment = StringField("Your views about this project", validators=[DataRequired()])
    submit = SubmitField("Comment")

class GrievanceForm(FlaskForm):
    choices = ["Project", "Other"]
    user_choice = SelectField("Type of issue", choices=choices, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    phone_no = StringField("Phone number")
    grievance = StringField("Tell us about your issue", validators=[DataRequired()])
    submit = SubmitField("Send")
