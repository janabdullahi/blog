from crypt import methods
from email.mime import image
import os
import secrets
from urllib.parse import parse_qs
from wsgiref import validate
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from httplib2 import Response
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm,SearchForm
from flaskblog.models import User, Post, PostLike
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_approved=True).order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=4)
    searchForm=SearchForm()
    return render_template('home.html', posts=posts, searchForm=searchForm)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_password,
                    role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats Your Account Has Been Successfuly Created!', 'success')
        return redirect(url_for('login'))
    searchForm=SearchForm()
    return render_template('register.html', title='Register', form=form, searchForm=searchForm)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            #role
            if user.role == 3:
                return redirect(url_for('home'))

            next_page = request.args.get('next')  # args.get() is method get() for MultiDict,
            return redirect(next_page) if next_page else redirect(
                url_for('home'))
        else:
            flash('Please Enter Valid Email and Password', 'danger')
    searchForm=SearchForm()
    return render_template('login.html', title='Login', form=form, searchForm=searchForm)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    #we can use (f_name) or (_) in the next line
    # for taking the filename with and without extension = (f_ext),(_)
    _, f_ext = os.path.splitext(form_picture.filename)
    #os.path.splitext() method in Python is used to split the path name into a pair root and ext.
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    #by default its (125,125)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data

        if form.new_password.data and form.confirm_password.data:
            if form.new_password.data == form.confirm_password.data:
                new_hashed_password = bcrypt.generate_password_hash(
                    form.new_password.data).decode('utf-8')
                user = User.query.get(current_user.id)
                user.password = new_hashed_password
                db.session.commit()
                logout_user()
                flash('Your Account Updated Successfully!', 'success')
                return redirect(url_for('login'))
            else:
                flash('Your Password Does Not Matched!',
                      'danger')
                return redirect(url_for('account'))
        db.session.commit()
        flash('Your Account Has Been Updated Successfully!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',
                         filename='profile_pics/' + current_user.image_file)
    searchForm = SearchForm()                    
    return render_template('account.html', title='Account',image_file=image_file,form=form, searchForm=searchForm)

@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
                .order_by(Post.date_posted.desc())\
                .paginate(page=page, per_page=5)
    searchForm = SearchForm()
    return render_template('user_posts.html', posts=posts, user=user, searchForm =searchForm )

def save_post_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    i = Image.open(form_picture)
    i.save(picture_path)
    return picture_fn


@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
            post = Post(title=form.title.data,short_description = form.short_description.data,
                        content=form.content.data,
                        author=current_user)
            if form.picture.data:
                picture_file = save_post_picture(form.picture.data)
                post.image_file = picture_file
            db.session.add(post)
            db.session.commit()
            flash('Your Post Has Been Created Successfully!', 'success')
            return redirect(url_for('home'))
    searchForm = SearchForm()        
    return render_template('create_post.html',title='New Post',form=form,legend='Create Post', searchForm =searchForm )

# @app.route("/post/<int:post_id>")
# @app.route("/post/<string:post_title>")
# def post(post_title):
#     post = Post.query.filter_by(title=post_title).first_or_404(post_title)
#     searchForm = SearchForm()
#     return render_template('post.html', title=post.title, post=post, searchForm =searchForm )

@app.route("/post/<string:slug>")
def post(slug):
    id=int(slug.split('-')[-1])
    post = Post.query.filter_by(id=id).first_or_404()
    searchForm = SearchForm()
    return render_template('post.html', title=post.title, post=post, searchForm =searchForm)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        if form.picture.data and post.image_file:
            pictures_path = os.path.join(app.root_path, 'static/profile_pics', post.image_file)
            os.remove(pictures_path)
            picture_file = save_post_picture(form.picture.data)
            post.image_file = picture_file
        post.title = form.title.data
        post.content = form.content.data
        post.short_description = form.short_description.data
        db.session.commit()
        flash(' Updated!', 'success')
        return redirect(url_for('post', slug=(post.title + '-' + str(post.id))))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        form.short_description.data = post.short_description
    searchForm = SearchForm()
    return render_template('create_post.html',
                           title='Update Post',
                           form=form,
                           legend='Edit Post', searchForm =searchForm )


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user and current_user.role != 1:
        abort(403)
    if post.image_file:
        pictures_path = os.path.join(app.root_path, 'static/profile_pics', post.image_file)
        os.remove(pictures_path)
    db.session.delete(post)
    db.session.commit()
    flash('Deleted!', 'success')
    searchForm = SearchForm()
    return redirect(url_for('home', searchForm =searchForm ))


@app.route('/like/<int:post_id>/<reaction>')
@login_required
def like_action(post_id, reaction):
    post = Post.query.filter_by(id=post_id).first_or_404()
    if reaction == 'like':
        current_user.like_post(post)
        db.session.commit()
    if reaction == 'unlike':
        current_user.unlike_post(post)
        db.session.commit()
    return redirect(
        request.referrer)  # referrer contains the address of the previous web page from


@app.route("/approvals")
def approvals():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_approved=False).order_by(
        Post.date_posted.desc()).paginate(page=page, per_page=4)
    searchForm = SearchForm()
    return render_template('approvals_posts.html', posts=posts, searchForm =searchForm )


@app.route("/post/<int:post_id>/approve", methods=['GET', 'POST'])
@login_required
def approve_post(post_id):
    post = Post.query.filter_by(id=post_id).first_or_404(post_id)

    form = PostForm()
    post.is_approved = True
    db.session.commit()
    flash('Your Post Has Been Approved Successfully!', 'success')
    # searchForm = SearchForm()
    return redirect(url_for('approvals'))


@app.route("/search", methods=['GET', 'POST'])
def search():
    form = SearchForm()
    if form.validate_on_submit():
        page = request.args.get('page', 1, type=int)
        posts = Post.query.filter(Post.title.like
            ("%" + form.searched.data + "%")).filter(Post.is_approved == True).order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    searchForm = SearchForm()
    return render_template('home.html', posts=posts, searchForm = searchForm)
    

@app.context_processor
def utility_processor():
    # Generate slug=title+id
    def slug(post):
        return post.title.replace(' ', '-') + '-' + str(post.id)
    return dict(slug=slug)