__author__ = 'GalihSuyoga'

# import required module
import os
# blueprint for managing route to several pythonfile, jsonify to return json value, render_template to render html page
from flask import request, Blueprint, jsonify
# flasgger for api documentation
from flasgger import swag_from
from main.model.text_processing import Abusive, KamusAlay, TextLog
# pandas for data manipulation
from main.cleanser import bersihkan_tweet_dari_file, bersihkan_tweet_dari_text
from sqlalchemy import or_
import pandas as pd

import re

from main.model import db

# initializing front root for project asset and template
gold = Blueprint('gold', __name__, template_folder='templates', static_folder='assets')


# @swag_from("docs/hello_swagger.yml", methods=['GET'])
# @gold.route('/hello-swagger', methods=['GET'])
# def gold_hello_swagger():
#     json_response = {
#         'status_code': 200,
#         'description': "Menyapa hallo Swagger",
#         'data': "Hallo Swagger"
#     }
#     return jsonify(json_response)


@swag_from("docs/text_processing.yml", methods=['POST'])
@gold.route('/gold-text-processing', methods=['POST'])
def gold_text_processing():
    text = request.form.get('text', '')
    json_response = {
        'status_code': 200,
        'raw_text': text,
        'cleaned_text': bersihkan_tweet_dari_text(text)
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
    array_text = []

    if file:
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
            abusive_df = pd.read_sql_query(
                sql=db.select([Abusive.word]),
                con=db.engine
            )
            alay_df = pd.read_sql_query(
                sql=db.select([KamusAlay.word, KamusAlay.meaning]),
                con=db.engine
            )
            for index, row in data_frame.iterrows():

                # existing = TextFileTweetLog.query.filter(TextFileTweetLog.tweet == text).first()
                # print(row.to_dict())
                # if existing is None:
                #     new_Tweet = TextFileTweetLog(tweet=text)
                #     new_Tweet.save()
                # print(text)
                # print()
                array_text.append(bersihkan_tweet_dari_file(tweet=str(row['Tweet']), df_abusive=abusive_df,
                                                            df_alay=alay_df, full=row.to_dict()))
    else:
        http_code = 400
        description = "file not found"

    json_response = {
        'status_code': http_code,
        'description': description,
        'data': array_text
    }
    return jsonify(json_response)


@swag_from("docs/text_adding_alay.yml", methods=['POST'])
@gold.route('/gold-text-tambah-kata-alay', methods=['POST'])
def gold_text_tambah_kata_alay():
    alay_text = request.form.get('alay', '').lower()
    meaning_text = request.form.get('meaning', '').lower()
    raw_text = {
        'alay': alay_text,
        'meaning': meaning_text
    }
    description = "Successfully updated"
    status_code = 200

    existing = KamusAlay.query.filter(or_(KamusAlay.word.in_([alay_text, meaning_text]), KamusAlay.meaning == alay_text,
                                          )).first()
    if existing:
        if existing.word == alay_text:
            description = f"alay word {existing.word} is already registered with meaning {existing.meaning}"
            status_code = 400
        elif existing.meaning == alay_text:
            description = f"alay word {alay_text} is registered as meaning of {existing.word}"
            status_code = 400
        elif existing.word == meaning_text:
            description = f"meaning word {meaning_text} is registered as alay word, which has meaning {existing.meaning}"
            status_code = 400
    else:
        abusise = Abusive.query.filter(Abusive.word == alay_text).first()
        if abusise:
            description = f"alay word {alay_text} is registered as abusive word"
            status_code = 400
        else:
            # save new alay word
            new_alay = KamusAlay(words=alay_text, meaning=meaning_text)
            new_alay.save()

    json_response = {
        'status_code': status_code,
        'description': description,
        'raw': raw_text
    }
    return jsonify(json_response)


@swag_from("docs/text_adding_abusive.yml", methods=['POST'])
@gold.route('/gold-text-tambah-kata-abusive', methods=['POST'])
def gold_text_tambah_kata_abusive():
    abuse_text = request.form.get('abuse', '').lower()

    description = "Successfully updated"
    status_code = 200

    word_is_alay = KamusAlay.query.filter(KamusAlay.word == abuse_text).first()

    if word_is_alay:

        description = f"{abuse_text} word is registered as alay word, see kbbi for more info"
        status_code = 400
    else:
        duplicate = Abusive.query.filter(Abusive.word == abuse_text).first()
        if duplicate:
            description = f"{abuse_text} word is already registered as abusive word"
            status_code = 400
        else:

            new_abusive = Abusive(words=abuse_text)
            new_abusive.save()

    json_response = {
        'status_code': status_code,
        'description': description,
        'raw': abuse_text
    }
    return jsonify(json_response)


@swag_from("docs/text_get_all_record.yml", methods=['GET', 'POST'])
@gold.route('/gold-text-ambil-semua-record', methods=['GET', 'POST'])
def gold_text_ambil_semua_record():
    description = "All recorded data"
    if request.method == "POST":
        query_text = request.form.get('query', '').lower()
        # print(query_text)
        description = f"Query kata {query_text}"
        search_manipulate = "%{}%".format(query_text)
        record_df = pd.read_sql_query(
            sql=db.select([TextLog.raw_text, TextLog.clean]).filter(TextLog.raw_text.ilike(search_manipulate)),
            con=db.engine
        )

    else:
        record_df = pd.read_sql_query(
            sql=db.select([TextLog.raw_text, TextLog.clean]),
            con=db.engine
        )

    data = record_df.to_json(orient="records")
    # print(data)
    json_response = {
        'status_code': 200,
        'description': description,
        'data': data
    }

    return jsonify(json_response)
