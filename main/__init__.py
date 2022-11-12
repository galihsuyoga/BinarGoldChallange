__author__ = 'GalihSuyoga'

# import required Module
import os
from flask import Flask, request, g
# import blueprint front
from main.frontend import front
from main.gold_challenge_api import gold
from main.model import db
from flasgger import Swagger, LazyString, LazyJSONEncoder
# using sqlalchemy so the data can be treated as model
from flask_sqlalchemy import SQLAlchemy
basedir = os.path.abspath(os.path.dirname(__file__))


# initiate Flask as app
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

DB_URI = 'sqlite:///' + os.path.join(basedir, 'database/gold.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
db = SQLAlchemy(app)


swagger_template = dict(
    info={
        'title': LazyString(lambda: 'API Documentation for Binar Gold Challenge'),
        'version': LazyString(lambda: '1.0.0'),
        'description': LazyString(lambda: 'API Documentation for Binar Gold Challenge ata Processing and Modeling'),
    },
    host=LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "docs",
            "route": "/docs.json"
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger = Swagger(app, template=swagger_template, config=swagger_config)

app.register_blueprint(front)
app.register_blueprint(gold)


# function agar db connection diclose jika context selesai
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     # jika db masih terbuka
#     if db is not None:
#         # menutup koneksi
#         db.close()
