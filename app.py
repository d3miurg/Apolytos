from flask import Flask
from config import Configuration
from flask_sqlalchemy import SQLAlchemy
from flask_sock import Sock

application = Flask(__name__)
application.config.from_object(Configuration)
database = SQLAlchemy(application)