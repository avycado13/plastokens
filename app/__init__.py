import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, current_app, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_security import (
    Security,
    SQLAlchemyUserDatastore,
    hash_password,
)
from flask_security.models import fsqla_v3 as fsqla
from config import Config
from app import models, extensions


migrate = Migrate()
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    extensions.db.init_app(app)
    migrate.init_app(app, extensions.db)
    mail.init_app(app)
    user_datastore = SQLAlchemyUserDatastore(extensions.db, models.User, models.Role)
    security = Security(app, user_datastore)  # noqa: F841
    app.config["REMEMBER_COOKIE_SAMESITE"] = "strict"
    app.config["SESSION_COOKIE_SAMESITE"] = "strict"

    # As of Flask-SQLAlchemy 2.4.0 it is easy to pass in options directly to the
    # underlying engine. This option makes sure that DB connections from the
    # pool are still valid. Important for entire application since
    # many DBaaS options automatically close idle connections.
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)
    with app.app_context():
        if os.path.exists("instance/test.db"):
            os.remove("instance/test.db")
        # Create User to test with
        extensions.db.create_all()
        if not security.datastore.find_user(email="test@me.com"):
            security.datastore.create_user(
                email="test@me.com", password=hash_password("password"), balance=1000
            )
        if not security.datastore.find_user(email="test@you.com"):
            security.datastore.create_user(
                email="test@you.com", password=hash_password("password"), balance=1000
            )
        extensions.db.session.commit()
    return app
