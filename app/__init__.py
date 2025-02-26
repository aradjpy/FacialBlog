from flask import Flask
from flask_login import LoginManager
from flask import Flask, request, current_app
from app.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_babel import Babel, lazy_gettext as _l


# login = LoginManager()

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'Login'
login.login_message = _l('Please log in to access this page.')
mail = Mail()
bootstrap = Bootstrap()
babel = Babel()


def create_app(config_class=config):
    app = Flask(__name__)
    app.config.from_object(Config)

    

    login.init_app(app) 
    login.login_view = 'main.login'

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    babel.init_app(app)

    
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)


    with app.app_context():
        db.create_all()


        if not current_app.debug:
            if app.config['MAIL_SERVER']:
                auth = None
                if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                    auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                secure = None
                if app.config['MAIL_USE_TLS']:
                    secure = ()
                mail_handler = SMTPHandler(
                    mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                    fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                    toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                    credentials=auth, secure=secure)
                mail_handler.setLevel(logging.ERROR)
                app.logger.addHandler(mail_handler)
        
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/YRN.log', maxBytes=10240,
                                            backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

            app.logger.setLevel(logging.INFO)
            app.logger.info('YRN startup')

        
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': models.User}

    return app