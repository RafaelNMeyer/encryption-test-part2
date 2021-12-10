import os,sqlite3
from controller.authGoogleController import authGoogle
from controller.indexController import indexControl
from manager.userManager import run_userManager
from database.db import init_db_command
from flask import Flask

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

try:
    init_db_command()
except sqlite3.OperationalError:
    pass

run_userManager(app)

app.register_blueprint(authGoogle)
app.register_blueprint(indexControl)


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
    