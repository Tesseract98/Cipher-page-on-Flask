from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from wtforms_alchemy import ModelForm
from wtforms import StringField, validators
from flask_login import LoginManager, UserMixin, login_required, current_user
from control.MainPage import main_page_api

app = Flask(__name__, template_folder='C:/Users/user/PycharmProjects/CipherOnFlask/view')
app.register_blueprint(main_page_api)
app.config.update(
    DEBUG=True,
    SECRET_KEY='!Very long key!',
    SQLALCHEMY_DATABASE_URI='sqlite:///C:/Users/user/PycharmProjects/CipherOnFlask/model/Users.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    WTF_CSRF_ENABLED=False
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String, nullable=False)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '{} {}'.format(self.id, self.user)


class UsersForm(ModelForm):
    class Meta:
        model = Users

    user = StringField(validators=[
        validators.length(max=50)
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
        pass


if __name__ == '__main__':
    db.drop_all()
    db.create_all()
    u_admin = Users(user='admin', password=generate_password_hash('admin'))
    db.session.add(u_admin)
    db.session.commit()
    app.run(host='localhost', port=5000)
