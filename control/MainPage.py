from cipher_classes.Rot47_modificated import RotModificated
from flask import Blueprint, request, render_template, abort

main_page_api = Blueprint('main_page_api', __name__)


@main_page_api.route('/main', methods=['GET', 'POST'])
# @login_required
def home():
    if request.method == 'GET':
        return render_template('main.html', cipher_text="", decipher_text="")
    elif request.method == 'POST':
        str_cipher_text = ''
        str_decipher_text = ''
        if 'decipher_text' in request.form:
            str_decipher_text = request.form['decipher_text']
        if 'cipher_text' in request.form:
            str_cipher_text = request.form['cipher_text']
        cipher = RotModificated("hello", 1)
        int_click, int_clear = 0, 0
        if 'btn_click' in request.form:
            int_click = int(request.form['btn_click'])
        if 'btn_clear' in request.form:
            int_clear = int(request.form['btn_clear'])
        if int_click == 1:
            str_cipher_text = cipher.encrypt(request.form['decipher_text'])
            return render_template('main.html', cipher_text=str_cipher_text, decipher_text=str_decipher_text)
        elif int_click == 2:
            str_decipher_text = cipher.decipher(request.form['cipher_text'])
            return render_template('main.html', cipher_text=str_cipher_text, decipher_text=str_decipher_text)
        elif int_clear == 1:
            return render_template('main.html', cipher_text=str_cipher_text, decipher_text="")
        elif int_clear == 2:
            return render_template('main.html', cipher_text="", decipher_text=str_decipher_text)
        abort(404)
