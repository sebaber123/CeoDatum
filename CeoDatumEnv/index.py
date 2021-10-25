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

from resources import user, visualization, home

app.add_url_rule('/', 'home', user.index)

app.add_url_rule('/graphLine/<database>&<x_axie>', 'graph_line', visualization.graphLine, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/graphLine/<database>&<x_axie>&<condition>', 'graph_line', visualization.graphLine, methods=['GET'])

app.add_url_rule('/graphBar/<database>&<x_axie>', 'graph_bar', visualization.graphBar, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/graphBar/<database>&<x_axie>&<condition>', 'graph_bar', visualization.graphBar, methods=['GET'])

app.add_url_rule('/dataTable/<database>&<rowName>&<column>', 'data_table', visualization.data_table, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/dataTable/<database>&<rowName>&<column>&<condition>', 'data_table', visualization.data_table, methods=['GET'])

app.add_url_rule('/pieChart/<database>&<rowName>', 'pie_chart', visualization.pie_chart, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/pieChart/<database>&<rowName>&<condition>', 'pie_chart', visualization.pie_chart, methods=['GET'])



app.add_url_rule('/plotter/<int:Bid>', 'plotter', visualization.plotter, methods=['GET'])
app.add_url_rule('/plotter/<database>&<column>', 'ajax_get_column_data', visualization.ajaxGetColumnData, methods=['GET'])

app.add_url_rule('/dragAndDrop', 'dragAndDrop', home.dragAndDrop, methods=['GET'])
app.add_url_rule('/dragAndDrop/uploadFile', 'uploadFile', home.uploadFile, methods=['POST'])
app.add_url_rule('/dragAndDrop/configurateUpload', 'configurateUpload', home.configurateUpload, methods=['POST'])

