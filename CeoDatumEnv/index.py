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

from resources import user, visualization, home, socialGraph
from resources.activities import activities
from resources.datasets import datasets

app.add_url_rule('/', 'home', user.index)

app.add_url_rule('/graphLine/<database>&<x_axie>', 'graph_line', visualization.graphLine, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/graphLine/<database>&<x_axie>&<condition>', 'graph_line', visualization.graphLine, methods=['GET'])

app.add_url_rule('/graphBar/<database>&<x_axie>', 'graph_bar', visualization.graphBar, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/graphBar/<database>&<x_axie>&<condition>', 'graph_bar', visualization.graphBar, methods=['GET'])

app.add_url_rule('/dataTable/<database>&<rowName>&<column>', 'data_table', visualization.data_table, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/dataTable/<database>&<rowName>&<column>&<condition>', 'data_table', visualization.data_table, methods=['GET'])

app.add_url_rule('/pieChart/<database>&<rowName>', 'pie_chart', visualization.pie_chart, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/pieChart/<database>&<rowName>&<condition>', 'pie_chart', visualization.pie_chart, methods=['GET'])


app.add_url_rule('/dotChart/<database>&<rowName>&<column>', 'dot_chart', visualization.dot_chart, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/dotChart/<database>&<rowName>&<column>&<condition>', 'dot_chart', visualization.dot_chart, methods=['GET'])

app.add_url_rule('/scatterChart/<database>&<rowName>&<column>&<dispersionX>&<dispersionY>', 'scatter_chart', visualization.scatter_chart, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/scatterChart/<database>&<rowName>&<column>&<dispersionX>&<dispersionY>&<condition>', 'scatter_chart', visualization.scatter_chart, methods=['GET'])


app.add_url_rule('/loginForm', 'loginForm', user.login_form, methods=['GET'])
app.add_url_rule('/login', 'login', user.login, methods=['POST'])

app.add_url_rule('/registerForm', 'registerForm', user.register_form, methods=['GET'])
app.add_url_rule('/register', 'register', user.register, methods=['POST'])

app.add_url_rule('/forgotPassword', 'forgotPassword', user.forgotPassword, methods=['GET'])

app.add_url_rule('/plotter/<int:Bid>', 'plotter', visualization.plotter, methods=['GET'])
app.add_url_rule('/plotter/<database>&<column>', 'ajax_get_column_data', visualization.ajaxGetColumnData, methods=['GET'])

app.add_url_rule('/dragAndDrop', 'dragAndDrop', home.dragAndDrop, methods=['GET'])
app.add_url_rule('/dragAndDrop/uploadFile', 'uploadFile', home.uploadFile, methods=['POST'])
app.add_url_rule('/dragAndDrop/configurateUploadCSV', 'configurateUploadCSV', home.configurateUploadCSV, methods=['POST'])
app.add_url_rule('/dragAndDrop/configurateUploadJSON', 'configurateUploadJSON', home.configurateUploadJSON, methods=['POST'])


app.add_url_rule('/activities', 'activities', activities.activities, methods=['GET'])

app.add_url_rule('/datasets', 'datasets', datasets.datasets, methods=['GET'])

#TWITTER
app.add_url_rule('/twitterSearch/<stringToSearch>&<int:topQuantity>&<int:articles>&<int:prep>', 'api_twitter_search', socialGraph.api_twitter_search, methods=['GET'])
app.add_url_rule('/twitter', 'twitter_search', socialGraph.twitter_search, methods=['GET'])

#INSPECT
app.add_url_rule('/inspectRows2', 'inspect_rows2', visualization.inspect_rows2, methods=['GET'])
app.add_url_rule('/inspectRows/<databaseId>&<objectString>', 'inspect_rows', visualization.inspect_rows, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/inspectRows/<databaseId>&<objectString>&<condition>', 'inspect_rows', visualization.inspect_rows, methods=['GET'])