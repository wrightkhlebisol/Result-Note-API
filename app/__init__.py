from config import Config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
import rq
import logging
from logging.handlers import RotatingFileHandler
import os

from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
    }
)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()
cors = CORS()
limiter = Limiter(
    key_func=get_remote_address, default_limits=["200 per day", "50 per hour"]
)


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue("flask-api-queue", connection=app.redis)

    with app.app_context():
        db.init_app(app)

        # TODO: check if this is relevant for the template
        if db.engine.url.drivername == "sqlite":
            migrate.init_app(app, db, render_as_batch=True, compare_type=True)
        else:
            migrate.init_app(app, db, compare_type=True)

        ma.init_app(app)
        jwt.init_app(app)
        cors.init_app(app)
        limiter.init_app(app)

    from app.auth import bp as auth_bp
    from app.classes import bp as classes_bp
    from app.errors import bp as errors_bp
    from app.reports import bp as reports_bp
    from app.schools import bp as schools_bp
    from app.scores import bp as scores_bp
    from app.subjects import bp as subjects_bp
    from app.tasks import bp as tasks_bp
    from app.users import bp as users_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(errors_bp)
    app.register_blueprint(classes_bp, url_prefix="/api/classes")
    app.register_blueprint(reports_bp, url_prefix="/api/reports")
    app.register_blueprint(schools_bp, url_prefix="/api/schools")
    app.register_blueprint(scores_bp, url_prefix="/api/scores")
    app.register_blueprint(subjects_bp, url_prefix="/api/subjects")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    # Set the rate limit for all routes in the auth_bp blueprint to 1 per second
    limiter.limit("1 per minute")(auth_bp)

    # Set the debuging to rotating log files and the log format and settings
    if not app.debug:
        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/flask_api.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("Flask API startup")

    return app
