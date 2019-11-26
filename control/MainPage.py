from cipher_classes.Rot47_modificated import RotModificated
from flask import Blueprint, request, render_template

main_page_api = Blueprint('main_page_api', __name__)


@main_page_api.route('/main', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == 'GET':
        return render_template('main.html')
    elif request.method == 'POST':
        pass
