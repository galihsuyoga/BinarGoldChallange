__author__ = 'GalihSuyoga'

# import required module
import os
# blueprint for managing route to several pythonfile, jsonify to return json value, render_template to render html page
import re

from flask import request, Blueprint, jsonify, redirect, url_for

from flasgger import swag_from

import pandas as pd
# initializing front root for project asset and template
gold = Blueprint('gold', __name__, template_folder='templates', static_folder='assets')

@swag_from("docs/hello_swagger.yml", methods=['GET'])
@gold.route('/hello-swagger', methods=['GET'])
def gold_hello_swagger():
    json_response = {
        'status_code': 200,
        'description': "Menyapa hallo Swagger",
        'data': "Hallo Swagger"
    }
    return jsonify(json_response)


@swag_from("docs/text_processing.yml", methods=['POST'])
@gold.route('/gold-text-processing', methods=['POST'])
def gold_text_processing():
    text = request.form.get('text')

    json_response = {
        'status_code': 200,
        'description': "Text yang sudah diproses",
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', text)
    }
    return jsonify(json_response)


# api get data from api through a csv file
@swag_from("docs/text_processing_from_file.yml", methods=['POST'])
@gold.route('/gold-text-processing_from_file', methods=['POST'])
def gold_text_processing_from_file():
    description = "text sudah diproses"
    http_code = 200
    """get the file"""
    file = request.files.get('text')
    """split filename to get the file extension"""
    array_name = file.filename.split(".")
    file_ext = array_name[-1].lower()
    """make sure it was csv"""
    if file_ext != "csv":
        """if it's not csv"""
        description = "file is not csv"
        http_code = 400
    else:
        """if csv"""

        print(file)
        pd.read_csv()
        data_frame = pd.read_csv(file, encoding='latin-1')
        print(data_frame.head())

    json_response = {
        'status_code': http_code,
        'description': description,
        'data': "Invalid input file"
    }
    return jsonify(json_response)
