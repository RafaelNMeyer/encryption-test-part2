from model.user import User
from flask_login import LoginManager

def run_userManager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    # Flask-Login helper to retrieve a user from our db
    @login_manager.user_loader
    def load_user(user_id):
        return User.get(user_id)