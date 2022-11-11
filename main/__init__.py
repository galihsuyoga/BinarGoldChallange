__author__ = 'GalihSuyoga'

# import required Module
from flask import Flask, request, g
# import blueprint front
from main.frontend import front
from main.gold_challenge_api import gold

from flasgger import Swagger, LazyString, LazyJSONEncoder



# initiate Flask as app
app = Flask(__name__)
app.json_encoder = LazyJSONEncoder

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
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    # jika db masih terbuka
    if db is not None:
        # menutup koneksi
        db.close()
