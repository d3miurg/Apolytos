from flask import Flask
from config import cfg

app = Flask(__name__)
app.config.from_object(cfg)
