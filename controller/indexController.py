from flask import render_template, Blueprint
from flask_login import current_user

indexControl = Blueprint('authIndex', __name__, template_folder='templates', static_folder='static')

@indexControl.route("/")
def index():
    if current_user.is_authenticated:
        return render_template("logged.html", user=current_user.name, email=current_user.email)
    else:
        return render_template("index.html")