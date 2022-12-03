__author__ = 'GalihSuyoga'

# import required module
import pandas as pd
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from main.model import db
from sklearn import preprocessing as p
from main.model.text_processing import FileTextLog, AlayAbusiveFileLog
# blueprint for managing route to several pythonfile, jsonify to return json value, render_template to render html page
from flask import Blueprint, render_template, redirect, url_for, send_file
# initializing front root for project asset and template
front = Blueprint('front', __name__, template_folder='templates', static_folder='assets')


fig, ax = plt.subplots(figsize=(20, 10))
sns.set(style="darkgrid")

# index/landing page
@front.route('/', methods=['GET'])
def index():
    return render_template('frontend/index.html')


# url redirection to swagger documentation
@front.route('/gold_index', methods=['GET'])
def gold_index():
    return redirect(f"{url_for('front.index')}docs/")


# url analisis
@front.route('/gold-tweet-analysis/<int:type>', methods=['GET'])
def gold_analysis(type):

    if type == 1:
        return render_template('frontend/plot1.html', url=url_for('front.visualize_plot1'),
                               title="Normalize len of word from tweet Distribution Plot")
    elif type == 2:
        return render_template('frontend/plot1.html', url=url_for('front.visualize_plot2'),
                               title="15 Most Frequent Abusive Word")
    elif type == 3:
        return render_template('frontend/plot1.html', url=url_for('front.visualize_plot3'),
                               title="Most Frequent Hate speech Category")


@front.route('/visualize/plot1')
def visualize_plot1():
    fig, ax = plt.subplots(figsize=(20, 10))

    # ternyata ada kata2 yang terdaftar di abusive seperti sipit tidak ada flag abusive atau HSnya
    # query text yang ter log atau terdeteksi di alayabusivelog yang terdaftar sebagai mixed atau abusive
    # ada 3 tipe yaitu abusive, alay, dan mixed(kata alay yang ternyata artinya adalah abusive word)
    df_file = pd.read_sql_query(
        sql=db.select(
            [FileTextLog.ID, FileTextLog.Tweet, FileTextLog.Clean, AlayAbusiveFileLog.word, AlayAbusiveFileLog.clean])
            .join(AlayAbusiveFileLog, AlayAbusiveFileLog.file_upload_text_log_id == FileTextLog.ID)
            .filter(AlayAbusiveFileLog.foul_type != "ALAY"),
        con=db.engine
    )
    # 15 abusive clean word terbanyak
    # print(df_file['clean'].value_counts()[:15])
    # # 15 abusive raw word terbanyak
    # print(df_file['word'].value_counts()[:15])
    # #
    # print(df_file['Tweet'].value_counts()[:15])

    # coba assign word count
    df_new = (
        df_file
            .groupby('Tweet')
            .agg({'word': 'count'})  # jumlah abusivenya
            .sort_values('word', ascending=False)
            .reset_index()
            .assign(
            len_char=lambda x: x['Tweet'].str.len(),
            len_word=lambda x: x['Tweet'].str.split().str.len()  # jumlah katanya
        )
    )

    # jumlah tweet yang mengandung abusive dan hatespeech
    # print(df_new.head())
    # median
    # print(df_new.median(numeric_only=True))
    # q1
    q1 = df_new['len_word'].quantile(0.25)
    # print(q1)
    # q2
    q2 = df_new['len_word'].quantile(0.5)
    # print(q2)
    # q3
    q3 = df_new['len_word'].quantile(0.75)
    # print(q3)

    iqr = q3 - q1
    # print(iqr)
    limit = 1.5 * iqr
    lower_bound = q1 - limit
    upper_bound = q3 + limit

    # print(lower_bound)
    # hasilnya -13
    # print(upper_bound)
    # hasilnya 43
    # print(df_new['len_word'].max())
    # max ada di 52
    # berarti ada outlier

    df_remove = df_new[df_new['len_word'] < upper_bound]
    df_remove_outlier = df_remove[df_remove['len_word'] > lower_bound]
    min_max_scaler = p.MinMaxScaler()

    normalize_len_word = min_max_scaler.fit_transform(df_remove_outlier['len_word'].values.reshape(-1,1))
    df_with_norm = df_remove_outlier.assign(normalized=normalize_len_word.flatten())
    # print(df_with_norm)
    # print(df_with_norm['normalized'].skew())
    # print(df_with_norm['normalized'].mean())
    # print(df_with_norm['normalized'].median())
    sns.histplot(df_with_norm['normalized'], kde=True)

    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)

    return send_file(img, mimetype='img/png')

@front.route('/visualize/plot2')
def visualize_plot2():
    fig, ax = plt.subplots(figsize=(20, 10))

    # ternyata ada kata2 yang terdaftar di abusive seperti sipit tidak ada flag abusive atau HSnya
    # query text yang ter log atau terdeteksi di alayabusivelog yang terdaftar sebagai mixed atau abusive
    # ada 3 tipe yaitu abusive, alay, dan mixed(kata alay yang ternyata artinya adalah abusive word)
    df_file = pd.read_sql_query(
        sql=db.select(
            [FileTextLog.ID, FileTextLog.Tweet, FileTextLog.Clean, AlayAbusiveFileLog.word, AlayAbusiveFileLog.clean])
            .join(AlayAbusiveFileLog, AlayAbusiveFileLog.file_upload_text_log_id == FileTextLog.ID)
            .filter(AlayAbusiveFileLog.foul_type != "ALAY"),
        con=db.engine
    )
    # # 15 abusive clean word terbanyak
    xy = df_file['clean'].value_counts()[:15]

    x = list(xy.keys())
    y = list(xy.values)

    # # 15 abusive raw word terbanyak
    # print(df_file['word'].value_counts()[:15])
    # #
    # print(df_file['Tweet'].value_counts()[:15])
    sns.barplot(x=x, y=y)

    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)

    return send_file(img, mimetype='img/png')

@front.route('/visualize/plot3')
def visualize_plot3():
    fig, ax = plt.subplots(figsize=(20, 10))
    # ternyata ada kata2 yang terdaftar di abusive seperti sipit tidak ada flag abusive atau HSnya
    # query text yang ter log atau terdeteksi di alayabusivelog yang terdaftar sebagai mixed atau abusive
    # ada 3 tipe yaitu abusive, alay, dan mixed(kata alay yang ternyata artinya adalah abusive word)
    df_file = pd.read_sql_query(
        sql=db.select(
            [FileTextLog.ID, FileTextLog.Tweet, FileTextLog.Clean, FileTextLog.HS, FileTextLog.Abusive,
             FileTextLog.HS_Gender, FileTextLog.HS_Group, FileTextLog.HS_Individual, FileTextLog.HS_Race,
             FileTextLog.HS_Physical, FileTextLog.HS_Religion, FileTextLog.HS_Strong, FileTextLog.HS_Weak,
             FileTextLog.HS_Moderate, FileTextLog.HS_Other, AlayAbusiveFileLog.word, AlayAbusiveFileLog.clean])
            .join(AlayAbusiveFileLog, AlayAbusiveFileLog.file_upload_text_log_id == FileTextLog.ID)
            .filter(AlayAbusiveFileLog.foul_type != "ALAY"),
        con=db.engine
    )

    sums = df_file.select_dtypes(np.number).sum().rename('total')
    sums.pop('ID')
    # print(sums)
    x = list(sums.keys())
    y = list(sums.values)

    # print(x)
    # print(y)
    # # 15 abusive raw word terbanyak
    # print(df_file['word'].value_counts()[:15])
    # #
    # print(df_file['Tweet'].value_counts()[:15])
    sns.barplot(x=x, y=y)

    canvas = FigureCanvas(fig)
    img = io.BytesIO()
    fig.savefig(img)
    img.seek(0)
    return send_file(img, mimetype='img/png')
