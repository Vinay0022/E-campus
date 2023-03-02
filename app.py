import os
from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from datetime import date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from forms import CreateEventForm, RegisterForm, LoginForm, CommentForm, GrievanceForm
from flask_gravatar import Gravatar
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

my_email = "pythonisez@yahoo.com"
password = "jdqsxomgcvrttjvi"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

##CONNECT TO DB
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///campus.db'
#postgres://e_campus_nysh_user:DfhzcNtiUoNGaaDWJomXeTYFfoAymq4X@dpg-cftne69a6gdotcfm7p0g-a.oregon-postgres.render.com/e_campus_nysh
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
gravatar = Gravatar(
    app,
    size=100,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


##CONFIGURE TABLES

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String(250), unique=True, nullable=False)
    ay= db.Column(db.String(250), nullable=False)
    group1 = db.Column(db.String(250), unique=True, nullable=False)
    group2 = db.Column(db.String(250), unique=True, nullable=False)
    group3 = db.Column(db.String(250), unique=True, nullable=False)
    guide = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    #body = db.Column(db.Text, nullable=False)
    #img_url = db.Column(db.String(250), nullable=False)
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    comment = db.Column(db.Text, nullable=False)
    comment_author = relationship("User", back_populates="comments")
    parent_post = relationship("BlogPost", back_populates="comments")


#db.create_all()
#with app.app_context():
#            db.create_all()


@app.route('/')
def get_all_posts():
    if current_user.is_authenticated:
        posts = BlogPost.query.all()
        return render_template("index.html", all_posts=posts)
    else:
        flash("You need to login first!")
        return redirect("/login")


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        regex = r'\A\S+@\S+\Z'
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if user:
            flash("You've already signed up with that email, log in instead!", "error")
            return redirect(url_for('login'))
        if (re.fullmatch(regex, email)):
            hashed_salted_psw = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            new_user = User(
                name=form.name.data,
                email=email,
                password=hashed_salted_psw,
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('get_all_posts'))
        else:
            flash("Please enter a valid email", "error")
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("That email does not exist, please try again.", "error")
            return redirect(url_for('login', form=form))
        elif user and not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.', 'error')
            return redirect(url_for('login', form=form))
        login_user(user)
        return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    form = CommentForm()
    if current_user.is_authenticated:
        if form.validate_on_submit():
            comment = form.comment.data
            new_comment = Comment(
                comment=comment,
                comment_author=current_user,
                parent_post=requested_post
            )
            db.session.add(new_comment)
            db.session.commit()
        return render_template("post.html", post=requested_post, form=form)
    return render_template("post.html", post=requested_post, form=form)


@app.route("/grievance", methods=["GET", "POST"])
def contact():
    if current_user.is_authenticated:
        form = GrievanceForm()
        if form.validate_on_submit():
            user_choice = form.user_choice.data
            email = form.email.data
            phone_no = form.phone_no.data
            grievance = form.grievance.data
            reciever = "el.17.swayam.thanekar@gmail.com"
            with smtplib.SMTP("smtp.mail.yahoo.com") as connection:
                connection.starttls()
                connection.ehlo()
                connection.login(user=my_email, password=password)
                connection.sendmail(
                    from_addr=my_email,
                    to_addrs=reciever,
                    msg=f"Subject:{user_choice} Issue\n\nMy name is {current_user.name} and my issue is {grievance}\nYou can contact me"
                        f" through the below given details:\nPhone No- {phone_no}\nEmail- {email}"
                )
            flash("Response has been submitted successfully!", "success")
    else:
        flash("You need to login first!")
        return redirect("/login")
    return render_template("contact.html", form=form)


@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreateEventForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            ay=form.ay.data,
            group1=form.group1.data,
            group2=form.group2.data,
            group3=form.group3.data,
            guide=form.guide.data,
            #body=form.body.data,
            #img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreateEventForm(
        title=post.title,
        ay=post.ay,
        group1=post.group1,
        group2=post.group2,
        group3=post.group3,
        guide=post.guide,
        #img_url=post.img_url,
        author=current_user,
        #body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.ay= edit_form.ay.data
        post.group1 = edit_form.group1.data
        post.group2 = edit_form.group2.data
        post.group3 = edit_form.group3.data
        post.guide = edit_form.guide.data
        #post.img_url = edit_form.img_url.data
        #post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))

    return render_template("make-post.html", form=edit_form)


@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))





if __name__ == "__main__":
    app.run(debug=True)
