from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.activity import Activity
from models.dataset import Dataset
from models.course import Course
from models.user import User
from datetime import date
import datetime


def activities():
	if session['name']:
		activities = Activity.getMyActivities(session['id'])
		finished_activities = []
		current_activities = []
		overdue_activities = []
		undelivered_activities = []
		corrected_activities = []
		for activity in activities:
			if activity['calification']:
				corrected_activities.append(activity)
			else: 
				if not activity['enable_expired_date'] and (activity['end_date'].strftime('%d-%m-%y')<date.today().strftime('%d-%m-%y')):
					undelivered_activities.append(activity)
				else:
					if activity['commentary']:
						finished_activities.append(activity)
					else:
						if activity['enable_expired_date'] and (activity['end_date'].strftime('%d-%m-%y')<date.today().strftime('%d-%m-%y')):
							overdue_activities.append(activity)
						else:
							current_activities.append(activity)
		return render_template('activities/activities.html', activities=activities, current_activities=current_activities, finished_activities=finished_activities, overdue_activities=overdue_activities, undelivered_activities=undelivered_activities, corrected_activities=corrected_activities, today=date.today())
	else:
		return render_template('/')

def new_activity(course_id):
	if session['actualRole'] == "professor":
		graficos = Activity.get_graph_names()

		datasets = datasets = Course.get_dataset_by_courseId(course_id)

		students = User.get_user_from_course(course_id)

		return render_template('activities/new_activity.html', course_id=course_id, graphs=graficos, datasets=datasets, students=students)
	else:
		return redirect(url_for('home'))

def create_activity():
	if request.method=="POST":
		titulo = request.form['title']
		fecha_comienzo = request.form['startDate']
		fecha_fin = request.form['endDate']
		descripcion = request.form['description']
		curso = request.form['course']
		graphs = request.form.getlist('graph')
		objective = request.form['objective']
		has_calification = 'checkboxNoCalification' in request.form
		enable_expired_date = 'checkboxExpiredDate' in request.form
		statement = request.form['inputStatement']
		statemenet_title = request.form['inputStatementTitle']
		student_select = request.form['student_select']
		students_id = request.form.getlist('student_checkbox')
		datasetId = request.form['datasetSelect']
		socialGraph = False
		if request.form.get('checkboxSocialGraph'):
			socialGraph = request.form.get('checkboxSocialGraph')
			if socialGraph == 'on':
				socialGraph = True
		Activity.create_activity(fecha_comienzo, fecha_fin, titulo, descripcion, curso, graphs, objective, has_calification, enable_expired_date, statemenet_title, statement, students_id, datasetId, socialGraph)
		return redirect(url_for('courses'))
	return redirect(url_for('home'))

def view_activity_data(id):
	if session['id']:
		actividad = Activity.get_activity_by_id(id)
		graficos_disponibles = Activity.get_graph_of_activity_by_id(id)
		return render_template('activities/activity_view_data.html', activity=actividad, available_graphs=graficos_disponibles)

def view_activity(id):
	if session['id']:
		actividad = Activity.get_activity_by_id(id)
		return render_template('activities/activity_view.html', activity=actividad, noNav=True)

def solveActivity(id):
	if session['id']:
		activity = Activity.get_activity_by_id(id)
		datasetId= activity['dataset_id']
		socialGraph = activity['social_graph']

		resolutions = Activity.get_user_activity_resolution(session['id'], id)



		graphs = Activity.get_graph_of_activity_by_id(id)
		plotterTab = len(graphs) != 0

		return render_template('activities/solve_activity.html', activity=activity, activityId=id, datasetId=datasetId, noNav=True, socialGraph=socialGraph, plotterTab=plotterTab, resolutions=resolutions)

def addPlotterResolutionToActivity():

	if request.method=="POST":

		#information of resolution
		commentary = request.form['commentary']
		activityId = request.form['activityId']
		userId = session['id']
		resolutionType = 'plotter'
		dateTimeNow = datetime.datetime.now()


		resolution_id = Activity.inset_resolution(activityId, userId, resolutionType, dateTimeNow ,commentary)


		
		#Information of plotter resolution
		y_axis = ''
		stringCondition = ''

		selection = request.form['selection']
		x_axis = request.form['x_axis']

		plotterResolutionFields='graph_type, x_axis'
		plotterResolutionFieldsValues = '\''+selection + '\', \'' + x_axis


		if request.form.get('y_axis'):

			y_axis = request.form['y_axis']

			plotterResolutionFields= plotterResolutionFields + ', y_axis'
			plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + y_axis



		dispersion_x = request.form['dispersion_x']
		dispersion_y = request.form['dispersion_y']
		cumulative = request.form['cumulative']
		has_condition = request.form['has_condition']
		datasetId = request.form['datasetId']	

		plotterResolutionFields= plotterResolutionFields + ', dispersion_x, dispersion_y, cumulative, has_condition, id_dataset, id_resolution'
		plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + dispersion_x
		plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + dispersion_y
		plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + str(cumulative)
		plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + str(has_condition)
		plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + str(datasetId)
		plotterResolutionFieldsValues = plotterResolutionFieldsValues + '\', \'' + str(resolution_id)+'\''


		plotter_resolution_id = Activity.insert_resolution_plotter(plotterResolutionFields, plotterResolutionFieldsValues)

		

		#Conditions
		if has_condition:

			stringCondition = request.form['stringCondition']

			Activity.insert_resolution_plotter_conditions(stringCondition, plotter_resolution_id)



	return ''

def addSocialGraphResolutionToActivity():

	if request.method=="POST":

		#information of resolution
		commentary = request.form['commentary']
		activityId = request.form['activityId']
		userId = session['id']
		resolutionType = 'social graph'
		dateTimeNow = datetime.datetime.now()

		resolution_id = Activity.inset_resolution(activityId, userId, resolutionType, dateTimeNow ,commentary)

		#Information of social graph resolution

		searchString = request.form['searchString']
		excludePrepositions = request.form['excludePrepositions']
		excludeArticles = request.form['excludeArticles']
		excludePronouns = request.form['excludePronouns']
		excludeConjunctions = request.form['excludeConjunctions']
		excludeAdverbs = request.form['excludeAdverbs']
		excludeVerbs = request.form['excludeVerbs']
		excludeLinks = request.form['excludeLinks']
		quantityOfWords = request.form['quantityOfWords']

		Activity.insert_resolution_social_graph(resolution_id, searchString, excludePrepositions, excludeArticles, excludePronouns, excludeConjunctions, excludeAdverbs, excludeVerbs, excludeLinks, quantityOfWords)






	return ''


def viewResolutionGraph(resolutionId):

	resolution = Activity.get_resolution(resolutionId)

	plotterResolution = Activity.get_plotter_resolution(resolutionId)

	dataset = Dataset.get_dataset(plotterResolution['id_dataset'])

	datasetName = dataset['name']

	plotterResolution['x_axis_to_show'] = plotterResolution['x_axis'].split('***')[len(plotterResolution['x_axis'].split('***'))-1] 

	if plotterResolution['y_axis']:

		plotterResolution['y_axis_to_show'] = plotterResolution['y_axis'].split('***')[len(plotterResolution['y_axis'].split('***'))-1] 

	plotterResolutionConditions	= []

	if plotterResolution['has_condition']:

		plotterResolutionConditions = Activity.get_plotter_resolution_conditions(plotterResolution['id_resolution_plotter'])

		for condition in plotterResolutionConditions:

			stringConditionField = condition['condition']

			stringCondition = ''

			if ' >= ' in stringConditionField and ' <= ' in stringConditionField:

				stringCondition =  stringConditionField.split('***')[1]

				stringCondition = stringCondition.split(' and ')[0]

				stringCondition = stringCondition + ' y ' + stringConditionField.split('***')[len(stringConditionField.split('***'))-1]

				

			else:

				stringCondition	= stringConditionField.split('***')[len(stringConditionField.split('***'))-1]

			condition['stringCondition'] = stringCondition	





	return render_template('activities/view_resolution_graph.html', noNav=True, datasetName=datasetName, plotterResolution=plotterResolution, conditions=plotterResolutionConditions )

def viewResolutionSocialGraph(resolutionId):

	resolution = Activity.get_resolution(resolutionId)

	socialGraphResolution = Activity.get_social_graph_resolution(resolutionId)

	return render_template('activities/view_resolution_social_graph.html', noNav=True, resolution=resolution, socialGraph=socialGraphResolution)