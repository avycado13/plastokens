import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask
from flask_security import (
    SQLAlchemyUserDatastore,
    hash_password,
)
from config import Config
from app import models, extensions


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    user_datastore = SQLAlchemyUserDatastore(extensions.db, models.User, models.Role)
    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    extensions.mail.init_app(app)
    extensions.admin.init_app(app)
    extensions.security.init_app(app, user_datastore)
    extensions.toolbar.init_app(app)
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

    # FlaskAdmin views
    from app.admin import AdminView, TransactionView

    # Admin views
    extensions.admin.add_view(
        AdminView(models.User, extensions.db.session)
    )
    extensions.admin.add_view(AdminView(models.Role, extensions.db.session)
        )
    extensions.admin.add_view(AdminView(models.Transaction, extensions.db.session))
    # extensions.admin.add_view(
    #     TransactionView(models.Transaction, extensions.db.session)
    # )
    app.register_blueprint(main_bp)
    with app.app_context():
        extensions.db.create_all()
        admin_role = extensions.security.datastore.find_or_create_role(name="admin")
        user_role = extensions.security.datastore.find_or_create_role(name="user")
        test_user = extensions.security.datastore.find_user(email="test@me.com")
        if not test_user:
            test_user = extensions.security.datastore.create_user(
                email="test@me.com",
                password=hash_password("password"),
            )
        extensions.security.datastore.add_role_to_user(test_user, admin_role)
        extensions.db.session.commit()
