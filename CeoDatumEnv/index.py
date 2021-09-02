from os import path
from flask import Flask
import psycopg2
import psycopg2.extras
from db import get_db
import json

app = Flask(__name__)
app.run(debug=True)

#@app.route("/")
#def hello():
#    cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
#    query = "SELECT *  FROM public.user"
#    cursor.execute(query)
#    list_users = cursor.fetchall()
#    return json.dumps(list_users)

from resources import user

app.add_url_rule('/', 'home', user.index)
app.add_url_rule('/intento', 'intento', user.intento)