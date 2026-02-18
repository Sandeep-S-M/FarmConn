import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-this'
    # Use absolute path to instance folder
    # app/config.py -> app/ -> flask_app/ -> flask_app/instance/farmer_v2.db
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or '587')  # ← Fix: 587 NOT 25
    MAIL_USE_TLS = True 
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'sandeepsm314@gmail.com'
    MAIL_PASSWORD = os.environ.get('MAIL_USERNAME') or 'qisy lcqm kumt cslt'
    ADMINS = ['sandeepsm314@gmail.com']
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'instance', 'farmer_v2.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
