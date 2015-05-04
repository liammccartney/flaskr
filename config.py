import os
import dotenv

dotenv.load_dotenv(".env")

class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENDABLED = True
    SECRET_KEY = 'this-oughta-be-changed'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
