import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from elasticsearch import Elasticsearch
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel, lazy_gettext as _l
from config import Config
from celery import Celery, Task
import rq
from redis import Redis


def get_locale():
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])


#The main init for creating a celery factory is to have celery task run with Task class, and its also nice to have celery setup all in factory method
#Also it is important to note that these tasks will have flask application context, so that services like our database connections are available.
#def celery_init_app(app: Flask) -> Celery:
#   class FlaskTask(Task):
#       def __call__(self, *args: object, **kwargs: object) -> object:
#           with app.app_context():
#               return self.run(*args, **kwargs)

#   celery_app = Celery(app.name, task_cls=FlaskTask)
#   celery_app.config_from_object(app.config["CELERY"])
#   celery_app.set_default()
#   app.extensions["celery"] = celery_app
#   return celery_app


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    
    app.config.from_prefixed_env()
    # celery_init_app(app)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) if app.config['ELASTICSEARCH_URL'] else None
    app.redis = Redis.from_url(app.config['CACHE_HOST_URL'])
    app.task_queue = rq.Queue('microblog-tasks', connection=app.redis)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)

    if not app.debug:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='devyadav4211@gmail.com',
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        #10240bytes = 10kb, backupcount = 10 means 10 log files will be created once one log file is filled completed 
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')
    return app
'''
The bottom import is a well known workaround that avoids circular imports, a common problem with Flask applications.
'''
from app import models


'''The script above creates the application object as an instance of class Flask imported from the flask package. 
The __name__ variable passed to the Flask class is a Python predefined variable, which is set to the name of the module in which it is used.
 Flask uses the location of the module passed here as a starting point when it needs to load associated resources such as template files'''
