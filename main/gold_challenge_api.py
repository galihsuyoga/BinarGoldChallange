__author__ = 'GalihSuyoga'

# import required module
import os
# blueprint for managing route to several pythonfile, jsonify to return json value, render_template to render html page
from flask import request, Blueprint, jsonify
# flasgger for api documentation
from flasgger import swag_from
from main.model.text_processing import Abusive, KamusAlay, TextFileTweetLog
# pandas for data manipulation
from main.cleanser import bersihkan_tweet
import pandas as pd
import re

from main.model import db

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
        'raw_text': text,
        'cleaned_text': bersihkan_tweet(text)
    }
    return jsonify(json_response)


# api get data from api through a csv file
@swag_from("docs/text_processing_from_file.yml", methods=['POST'])
@gold.route('/gold-text-processing-from-file', methods=['POST'])
def gold_text_processing_from_file():

    description = "text sukses diproses"
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
        """masukkan csv ke panda dataframe variabel data_frame"""

        data_frame = pd.read_csv(file.stream, encoding='latin-1')
        # for data in data_frame:
        # print(data_frame['Abusive'])
        # data_frame.to_sql('kamus_alay', con=db.engine, if_exists='replace', index_label='id')
        # print(data_frame)
        array_text = []
        for index, row in data_frame.iterrows():
            # print(row['Tweet'])
            text = str(row['Tweet'])
            existing = TextFileTweetLog.query.filter(TextFileTweetLog.tweet == text).first()
            print(list[row])
            # if existing is None:
            #     new_Tweet = TextFileTweetLog(tweet=row['Tweet'])
            #     new_Tweet.save()'
            # print(text)
            # print()
            # array_text.append(bersihkan_tweet(text))

    json_response = {
        'status_code': http_code,
        'description': description,
        'data': array_text
    }
    return jsonify(json_response)
