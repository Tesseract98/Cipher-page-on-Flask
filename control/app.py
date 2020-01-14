import os
from datetime import datetime
from CipherPage import main_page_api
from flask import Flask, url_for, redirect, render_template, request, flash
from flask_admin import helpers, expose, AdminIndexView, Admin
from flask_login import LoginManager, logout_user, login_user, current_user, UserMixin, login_required
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_admin.contrib import sqla
from wtforms import validators, fields, StringField, form
from wtforms_alchemy import ModelForm

TEMPLATE_FOLDER_STR = "{}/{}".format(os.path.dirname(os.path.dirname(__file__)), 'view')
SQLITE_MODEL_PATH = "{}{}/{}".format('sqlite:///', os.path.dirname(os.path.dirname(__file__)), 'model/Users.db')

app = Flask(__name__, template_folder=TEMPLATE_FOLDER_STR)
app.register_blueprint(main_page_api)
app.config.update(
    SQLALCHEMY_DATABASE_URI=SQLITE_MODEL_PATH,
    DEBUG=True,
    SECRET_KEY=generate_password_hash('!key!'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=False,
    FLASK_ADMIN_SWATCH='cerulean',
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    login = db.Column(db.String(50), nullable=False)
    __password = db.Column(db.String(250), nullable=False)
    # email = db.Column(db.String(100), unique=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.__password = generate_password_hash(password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    def get_id(self):
        return self.id

    @property
    def password(self):
        return self.__password

    def check_password(self, password):
        return check_password_hash(self.__password, password)

    def __repr__(self):
        return '{} {}'.format(self.id, self.login)


def get_user(name: str):
    return db.session.query(Users).filter_by(login=name).first()


class UsersForm(ModelForm):
    class Meta:
        model = Users

    login = StringField(validators=[
        validators.DataRequired(),
        validators.length(min=3, max=50)
    ])
    password = StringField(validators=[
        validators.DataRequired(),
        validators.length(min=3, max=15)
    ])

    __user_from_db = None

    def validate_login(self, field):
        self.__user_from_db = get_user(field.data)

        if self.__user_from_db is None:
            raise validators.ValidationError('Invalid user')

        if self.login.data != self.__user_from_db.login:
            raise validators.ValidationError('Invalid login or password')

    def validate_password(self, field):
        if self.__user_from_db is not None:
            if not self.__user_from_db.check_password(self.password.data):
                raise validators.ValidationError('Invalid login or password')
            login_user(self.__user_from_db)


@app.route('/', methods=['GET', 'POST'])
def login_func():
    if request.method == 'GET':
        return render_template('authorization.html', btn_reg=True, form="")
    if request.method == 'POST':
        user_form = UsersForm(request.form)
        if user_form.validate():
            return redirect(url_for('main_page_api.home'))
        return render_template('authorization.html', btn_reg=True, form=user_form)


@app.route('/logout/')
def logout_func():
    logout_user()
    return redirect(url_for('login_func'))


def chk_pass(form_out, field):
    if form_out.password.data != field.data:
        raise validators.ValidationError('Not same check password')


class RegistrationUserForm(form.Form):
    login = fields.StringField(validators=[validators.DataRequired(),
                                           validators.length(min=3, max=15)])
    # email = fields.StringField()
    password = fields.PasswordField(validators=[validators.DataRequired(),
                                                validators.length(min=3, max=15)])
    chk_password = fields.PasswordField(validators=[chk_pass])

    def validate_login(self, field):
        if db.session.query(Users).filter_by(login=self.login.data).count() > 0:
            raise validators.ValidationError('Duplicate username')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('registration.html', form="")
    if request.method == 'POST':
        user_form = RegistrationUserForm(request.form)
        if user_form.validate():
            db_write = unbox_user_form(user_form)
            db.session.add(db_write)
            db.session.commit()
            flash('Successfully registration')
            login_user(db_write)
            return redirect(url_for('main_page_api.home'))
        return render_template('registration.html', form=user_form)


def unbox_user_form(user_form):
    user = Users(login=user_form.data['login'])
    user.set_password(user_form.data['password'])
    return user


# Define login and registration forms (for flask-login)
class LoginForm(form.Form):
    login = fields.StringField(validators=[validators.DataRequired()])
    password = fields.PasswordField(validators=[validators.DataRequired()])

    def validate_login(self, field):
        user = get_user('admin')

        if user is None:
            raise validators.ValidationError('Invalid user')

        # we're comparing the plaintext pw with the the hash from the db
        if not user.check_password(self.password.data) or self.login.data != user.login:
            # to compare plain text passwords use
            # if user.password != self.password.data:
            raise validators.ValidationError('Invalid login or password')


class MyAdminIndexView(AdminIndexView):
    admin_u = get_user('admin')

    @expose('/', methods=('GET', 'POST'))
    def index(self):
        if request.method == 'GET':
            if not current_user.is_authenticated or current_user != self.admin_u:
                return render_template('authorization.html', link='admin/', form='')
            return super(MyAdminIndexView, self).index()
        elif request.method == "POST":
            user_form = UsersForm(request.form)
            if user_form.validate():
                db_write = get_user(user_form.data['login'])
                if db_write == self.admin_u:
                    login_user(db_write)
                    return super(MyAdminIndexView, self).index()
            return render_template('authorization.html', link='admin/', form='')

    # Another one method of login
    # @expose('/login/', methods=('GET', 'POST'))
    # def login_view(self):
    #     # handle user login
    #     form_login = LoginForm(request.form)
    #     if helpers.validate_form_on_submit(form_login):
    #         login_user(get_user(form_login.data['login']))
    #
    #     if current_user.is_authenticated:
    #         return redirect(url_for('.index'))
    #     # link = '<p>Register <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
    #     self._template_args['form'] = form_login
    #     self._template_args['admin'] = get_user('admin')
    #     # self._template_args['link'] = link
    #     return super(MyAdminIndexView, self).index()

    @expose('/logout/')
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


# Create customized model view class
class MyModelView(sqla.ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


@app.route('/secure', methods=['GET', 'POST'])
@login_required
def db_writes():
    sup_user = get_user('sup')
    if request.method == 'GET':
        if current_user == sup_user:
            return render_template('TableOfUsers.html', user=Users.query.all())
        return render_template('authorization.html', link='secure', form='')
    elif request.method == 'POST':
        user_form = UsersForm(request.form)
        if user_form.validate():
            db_write = get_user(user_form.data['login'])
            if db_write == sup_user:
                login_user(db_write)
                # db.session.query(Users).all()
                return render_template('TableOfUsers.html', user=Users.query.all())
        return render_template('authorization.html', link='secure', form='')


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    test_user = Users(login="test")
    test_user.set_password('1234')
    db.session.add(test_user)

    first_names = [
        'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
        'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
        'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
    ]
    last_names = [
        'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
        'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
        'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
    ]

    for i in range(len(first_names)):
        user = Users()
        # user.first_name = first_names[i]
        # user.last_name = last_names[i]
        user.login = first_names[i].lower()
        # user.email = user.login + "@example.com"
        user.set_password(''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10)))
        db.session.add(user)

    db.session.commit()
    return


if __name__ == '__main__':
    # Create admin
    admin = Admin(app, 'Cipher project', index_view=MyAdminIndexView(), base_template='my_master.html')
    # Add view
    admin.add_view(MyModelView(Users, db.session))

    # db.drop_all()
    # db.create_all()
    # build_sample_db()
    # u_admin = Users(login='admin')
    # u_admin.set_password('admin')
    # u_assistant = Users(login='sup')
    # u_assistant.set_password('sup')
    # db.session.add_all([u_admin, u_assistant])
    # db.session.commit()

    app.run(host='localhost', port=5000)
