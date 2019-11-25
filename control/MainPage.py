from control.autification import app, request, login_required, render_template


@app.route('/main', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        pass
    elif request.method == 'POST':
        pass
