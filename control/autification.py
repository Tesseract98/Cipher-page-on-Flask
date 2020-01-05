import os.path as op
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms_alchemy import ModelForm
from wtforms import StringField, validators
from flask_login import LoginManager, UserMixin, login_required, current_user, login_user, logout_user
from MainPage import main_page_api
from flask_admin import Admin, AdminIndexView, expose, helpers
from flask_admin.contrib.sqla import ModelView

# from flask_security import UserMixin, RoleMixin
# from flask_security import SQLAlchemySessionUserDatastore, Security


template_folder_str = 'C:/Users/user/Documents/Python_projects/Cipher-page-on-Flask/view'
# template_folder_str = op.join(op.dirname(__file__), 'view')
sqlite_model_path = 'sqlite:///C:/Users/user/Documents/Python_projects/Cipher-page-on-Flask/model/Users.db'

app = Flask(__name__, template_folder=template_folder_str)
app.register_blueprint(main_page_api)
app.config.update(
    SQLALCHEMY_DATABASE_URI=sqlite_model_path,
    DEBUG=True,
    SECRET_KEY=generate_password_hash('!key!'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=False,
    FLASK_ADMIN_SWATCH='Darkly',
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
admin = Admin(app, name='cipher', template_mode='bootstrap3')


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


# roles_users = db.Table('roles_users',
#                        db.Column('users_id', db.Integer(), db.ForeignKey('users.id')),
#                        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    user = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(250), nullable=False)
    # email = db.Column(db.String(100), unique=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    # roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '{} {}'.format(self.id, self.user)


# class Role(db.Model, RoleMixin):
#     __tablename__ = 'role'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     name = db.Column(db.String(100), unique=True)
#     description = db.Column(db.String(255))


# user_datastore = SQLAlchemySessionUserDatastore(db, Users, Role)
# security = Security(app, user_datastore)

admin.add_view(ModelView(Users, db.session))


class UsersForm(ModelForm):
    class Meta:
        model = Users

    user = StringField(validators=[
        validators.DataRequired(),
        validators.length(max=50)
    ])
    password = StringField(validators=[
        validators.DataRequired(),
        validators.length(max=15)
    ])


@app.route('/users', methods=['GET'])
def user_db():
    if request.method == 'GET':
        # all_db_writes = Users.query.with_entities(Users.id, Users.user, Users.created_on)
        all_db_writes = Users.query.all()
        return render_template('TableOfUsers.html', user=all_db_writes)


@app.route('/', methods=['GET', 'POST'])
def log_in():
    if request.method == 'GET':
        return render_template('authorization.html')
    if request.method == 'POST':
        user_form = UsersForm(request.form)
        if user_form.validate():
            db_write = Users(**user_form.data)
            db.session.add(db_write)
            db.session.commit()
            flash('Logged in successfully.')
            login_user(db_write)
        return redirect(url_for('main_page_api.home'))


if __name__ == '__main__':
    print(template_folder_str)
    db.drop_all()
    db.create_all()
    # user_datastore.create_user(user='admin', password='admin')
    # db.session.add(user_datastore)
    u_admin = Users(user='admin', password=generate_password_hash('admin'))
    db.session.add(u_admin)
    db.session.commit()
    app.run(host='localhost', port=5000)
