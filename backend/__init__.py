import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)

app.config["SECRET_KEY"] = "mysecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@localhost/trailfinderflask'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
Migrate(app, db)

CORS(app)
