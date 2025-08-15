import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///hr_web.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
