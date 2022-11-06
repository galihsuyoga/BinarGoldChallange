__author__ = 'GalihSuyoga'

# import required module
import os
# blueprint for managing route to several pythonfile, jsonify to return json value, render_template to render html page
from flask import request, Blueprint, jsonify

from flasgger import swag_from
# initializing front root for project asset and template
gold = Blueprint('gold', __name__, template_folder='templates', static_folder='assets')


@swag_from("docs/hello_swagger.yml", methods=['GET'])
@gold.route('/gold', methods=['GET'])
def gold_hello_swagger():
    json_response = {
        'status_code': 200,
        'description': "Menyapa hallo Swagger",
        'data': "Hallo Swagger"
    }
    return jsonify(json_response)

