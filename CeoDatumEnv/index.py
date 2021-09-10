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

from resources import user, visualization

app.add_url_rule('/', 'home', user.index)
app.add_url_rule('/intentoLine', 'intento_line', visualization.intentoLine)
app.add_url_rule('/intentoBar/<x_axie>', 'intento_bar', visualization.intentoBar, methods=['GET'])
app.add_url_rule('/embebido/<int:Bid>', 'embebido', visualization.embebido, methods=['GET'])