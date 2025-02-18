import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = '587'
    MAIL_USE_TLS = 'True'
    MAIL_USERNAME = 'aradtestyrn@gmail.com'
    MAIL_PASSWORD = 'kddb kspj ortl udkn'
    ADMINS = ['aradforsure@gmail.com']
    LANGUAGES = ['en', 'fr','fa','es']
    POSTS_PER_PAGE = 5

