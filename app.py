from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config.from_object(Configuration)
database = SQLAlchemy(application)
