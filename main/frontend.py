__author__ = 'GalihSuyoga'

# import required module
import os
# blueprint for managing route to several pythonfile, jsonify to return json value, render_template to render html page
from flask import Blueprint, jsonify, render_template, redirect, url_for
# initializing front root for project asset and template
front = Blueprint('front', __name__, template_folder='templates', static_folder='assets')


# index/landing page
@front.route('/', methods=['GET'])
def index():
    return render_template('frontend/index.html')


# url redirection to swagger documentation
@front.route('/gold_index', methods=['GET'])
def gold_index():
    return redirect(f"{url_for('front.index')}docs/")