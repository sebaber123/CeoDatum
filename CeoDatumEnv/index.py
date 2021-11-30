from os import path
from flask import Flask
import psycopg2
import psycopg2.extras
from db import get_db
from flask_session import Session
import json

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
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
from resources.configuration import configuration

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
app.add_url_rule('/logout', 'logout', user.logout, methods=['GET'])


app.add_url_rule('/registerForm', 'registerForm', user.register_form, methods=['GET'])
app.add_url_rule('/showRegister', 'showRegister', user.show_register, methods=['GET'])
app.add_url_rule('/register', 'register', user.register, methods=['POST'])

app.add_url_rule('/forgotPassword', 'forgotPassword', user.forgotPassword, methods=['GET'])

app.add_url_rule('/plotter/<int:Bid>', 'plotter', visualization.plotter, methods=['GET'])
app.add_url_rule('/plotter/<database>&<column>', 'ajax_get_column_data', visualization.ajaxGetColumnData, methods=['GET'])

app.add_url_rule('/dragAndDrop', 'dragAndDrop', home.dragAndDrop, methods=['GET'])
app.add_url_rule('/dragAndDrop/uploadFile', 'uploadFile', home.uploadFile, methods=['POST'])
app.add_url_rule('/dragAndDrop/configurateUploadCSV', 'configurateUploadCSV', home.configurateUploadCSV, methods=['POST'])
app.add_url_rule('/dragAndDrop/configurateUploadJSON', 'configurateUploadJSON', home.configurateUploadJSON, methods=['POST'])


app.add_url_rule('/activities', 'activities', activities.activities, methods=['GET'])
app.add_url_rule('/activities/new_activity', 'new_activity', activities.new_activity)

app.add_url_rule('/datasets', 'datasets', datasets.datasets, methods=['GET'])

app.add_url_rule('/configuration', 'configuration', configuration.configuration, methods=['GET'])
app.add_url_rule('/update_establishment_file', 'update_establishment_file', configuration.upload_establishment_file, methods=['POST'])
app.add_url_rule('/cambiar_rol/<user_id>/<role_id>', 'cambiar_rol', configuration.cambiar_rol, methods=['GET'])

<<<<<<< HEAD
from resources.educational_establishments import extracting_data
app.add_url_rule('/get_establishments', 'get_establishments', extracting_data.extract_data, methods=['GET'])
app.add_url_rule('/showRegister/<province>', 'get_cities_by_province', extracting_data.get_cities_by_province, methods=['GET'])
app.add_url_rule('/showRegister/ciudad/<city>', 'get_establishment_by_city', extracting_data.get_establishments_by_city, methods=['GET'])
=======
app.add_url_rule('/datasets', 'datasets', datasets.datasets, methods=['GET'])

#TWITTER
app.add_url_rule('/twitterSearch/<stringToSearch>&<int:topQuantity>&<int:articles>&<int:prep>', 'api_twitter_search', socialGraph.api_twitter_search, methods=['GET'])
app.add_url_rule('/twitter', 'twitter_search', socialGraph.twitter_search, methods=['GET'])

#INSPECT
app.add_url_rule('/inspectRows2', 'inspect_rows2', visualization.inspect_rows2, methods=['GET'])
app.add_url_rule('/inspectRows/<databaseId>&<objectString>', 'inspect_rows', visualization.inspect_rows, methods=['GET'], defaults={'condition':None})
app.add_url_rule('/inspectRows/<databaseId>&<objectString>&<condition>', 'inspect_rows', visualization.inspect_rows, methods=['GET'])
>>>>>>> d1bc5cf1a91c626e8b137f2e4357ac2216f29994
