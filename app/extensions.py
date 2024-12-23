from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_security import Security
from flask_admin import Admin
from flask_debugtoolbar import DebugToolbarExtension

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
admin = Admin()
security = Security()
toolbar = DebugToolbarExtension()
