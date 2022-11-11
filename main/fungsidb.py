
# import flask global
from flask import g
# sqlite for local database creation
import sqlite3


# letak file database
DATABASE = '/database/gold.db'


# fungsi manggil DB
def get_db():

    db = getattr(g, '_database', None)
    # jika db kosong
    if db is None:
        # koneksikan database
        db = g._database = sqlite3.connect(DATABASE)
    return db


# fungsi query db terdiri dari string querynya, argumen/variablenya, dan flag apakah nyari yang pertama saja atau
# sebuah array
def query_db(query, args=(), one=False):
    # setup
    cur = get_db().execute(query, args)
    # ambil
    rv = cur.fetchall()
    # menutup koneksi
    cur.close()
    # ambil nilai pertama jika rv tidak kosong dan jika one is true, sisanya return apapun nilai rv
    return (rv[0] if rv else None) if one else rv


