from app import app, db
from flask import render_template, redirect, url_for, flash
from app.forms import SignUpForm, LoginForm, PhoneForm
from app.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', posts=posts)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        print('Hooray our form was validated!!')
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        username = form.username.data
        password = form.password.data
        print(first_name, last_name, email, username, password)
        check_user = db.session.execute(db.select(User).filter((User.username == username) | (User.email == email))).scalars().all()
        if check_user:
            flash("A user with that username and/or email already exists", "warning")
            return redirect(url_for('signup'))
        new_user = User(first_name=first_name, last_name=last_name, email=email, username=username, password=password)
        flash(f"Thank you {new_user.username} for signing up!", "success")
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print('Form Validated :)')
        username = form.username.data
        password = form.password.data
        print(username, password)
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            flash(f'You have successfully logged in as {username}', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username and/or password. Please try again', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash("You have logged out", "info")
    return redirect(url_for('index'))


@app.route('/add-phone', methods=["GET", "POST"])
@login_required
def add_phone():
    form = PhoneForm()
    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        address = form.address.data
        phone_number = form.phone_number.data
        new_phonebook = Post(first_name=first_name, last_name=last_name, address=address, phone_number=phone_number, user_id=current_user.id)
        flash(f"{new_phonebook.first_name} has been added to the phone book", "success")
        return redirect(url_for('index'))
    return render_template('createphonebook.html', form=form)

@app.route('/edit/<post_id>', methods=["GET", "POST"])
@login_required
def edit_post(post_id):
    form = PhoneForm()
    post_to_edit = Post.query.get_or_404(post_id)
    if post_to_edit.author != current_user:
        flash("You do not have permission to edit this post", "danger")
        return redirect(url_for('index'))

    if form.validate_on_submit():
        post_to_edit.first_name = form.first_name.data
        post_to_edit.last_name = form.last_name.data
        post_to_edit.address = form.address.data
        post_to_edit.phone_number = form.phone_number.data
        db.session.commit()
        flash(f"{post_to_edit.first_name} has been edited!", "success")
        return redirect(url_for('index'))

    form.first_name.data = post_to_edit.first_name
    form.last_name.data = post_to_edit.last_name
    form.address.data = post_to_edit.address
    form.phone_number.data = post_to_edit.phone_number
    return render_template('edit.html', form=form, post=post_to_edit)


@app.route('/delete/<post_id>')
@login_required
def delete_post(post_id):
    post_to_delete = Post.query.get_or_404(post_id)
    if post_to_delete.author != current_user:
        flash("You do not have permission to delete this post", "danger")
        return redirect(url_for('index'))

    db.session.delete(post_to_delete)
    db.session.commit()
    flash(f"{post_to_delete.first_name} has been deleted", "info")
    return redirect(url_for('index'))