import os
from flask import Config
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from celery import Celery
from oauthlib.oauth2 import WebApplicationClient
from .api.common.base_definitions import BaseFlask

# flask config
conf = Config(root_path=os.path.abspath(os.path.dirname(__file__)))
conf.from_object(os.getenv('APP_SETTINGS'))

# instantiate the extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()


def create_app():
    # instantiate the app
    app = BaseFlask(__name__)
    # set up extensions
    db.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)

    # register blueprints
    from .api.v1.auth import auth_blueprints
    from .api.v1.user import user_blueprints
    from .api.v1.admin import admin_blueprints

    blueprints = [*auth_blueprints, *user_blueprints, *admin_blueprints]
    for blueprint in blueprints:
        app.register_blueprint(blueprint, url_prefix='/v1')

    app.github_client = WebApplicationClient(app.config['GITHUB_CLIENT_ID'])
    app.facebook_client = WebApplicationClient(app.config['FACEBOOK_CLIENT_ID'])
    return app


def make_celery(app):
    app = app or create_app()
    # add include=['project.tasks.weather_tasks']
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'], include=['project.tasks.mail_tasks'],
                    backend=app.config['CELERY_RESULT_BACKEND'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


app = create_app()

# register error handlers
from werkzeug.exceptions import HTTPException

from .api.common.utils import exceptions
from .api.common import error_handlers

app.register_error_handler(exceptions.InvalidPayloadException, error_handlers.handle_exception)
app.register_error_handler(exceptions.BadRequestException, error_handlers.handle_exception)
app.register_error_handler(exceptions.UnauthorizedException, error_handlers.handle_exception)
app.register_error_handler(exceptions.ForbiddenException, error_handlers.handle_exception)
app.register_error_handler(exceptions.NotFoundException, error_handlers.handle_exception)
app.register_error_handler(exceptions.ServerErrorException, error_handlers.handle_exception)
app.register_error_handler(Exception, error_handlers.handle_general_exception)
app.register_error_handler(HTTPException, error_handlers.handle_werkzeug_exception)

celery = make_celery(app)
