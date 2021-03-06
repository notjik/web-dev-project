import flask
import flask_login
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
from PIL import Image

from data import db_session
from data.users import User
from data.jobs import Jobs
from data.services import Services
from data.branches import Branch
from data.register import RegisterForm
from data.login import LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Wrong login or password", form=form)
    return render_template('login.html', title='Authorization', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Register', form=form,
                                   message="Passwords don't match")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Register', form=form,
                                   message="This user already exists")
        user = User(
            email=form.email.data,
            nickname=form.nickname.data,
            surname=form.surname.data,
            name=form.name.data,
            speciality=form.speciality.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='??????????????????????', form=form)


@app.route('/preview/<int:id>')
def response_preview(id):
    db_sess = db_session.create_session()
    image = db_sess.query(Services).get(id)
    if image:
        return app.response_class(image.preview, mimetype='application/octet-stream')
    else:
        return flask.abort(404)


@app.route("/")
def index():
    db_sess = db_session.create_session()
    services = db_sess.query(Services).all()
    users = db_sess.query(User).all()
    names = {name.id: name.nickname for name in users}
    return render_template("index.html", services=services, names=names, title='Available vacancies')


@app.route("/myprofile")
def myprofile():
    if flask_login.current_user.is_authenticated:
        return render_template("myprofile.html", title='My profile')
    else:
        return redirect("/login")


if __name__ == '__main__':
    db_session.global_init("db/freelance_exchange.db")
    app.run()
