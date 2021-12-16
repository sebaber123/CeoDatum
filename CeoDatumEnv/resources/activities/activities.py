from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.activity import Activity
from models.course import Course
from models.user import User
from datetime import date


def activities():
	if session['name']:
		activities = Activity.getMyActivities(session['id'])
		
		return render_template('activities/activities.html', activities=activities, today=date.today())
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
		has_calification = request.form['checkboxNoCalification']
		enable_expired_date = request.form['checkboxExpiredDate']
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
		

		if has_calification == 1:
			has_calification=False
		else:
			has_calification=True
		if enable_expired_date == 1:
			enable_expired_date=True
		else:
			enable_expired_date = False
		Activity.create_activity(fecha_comienzo, fecha_fin, titulo, descripcion, curso, graphs, objective, has_calification, enable_expired_date, statemenet_title, statement, students_id, datasetId, socialGraph)
		return redirect(url_for('courses'))
	return redirect(url_for('home'))

def view_activity(id):
	if session['id']:
		actividad = Activity.get_activity_by_id(id)
		return render_template('activities/activity_view.html', activity=actividad, noNav=True)

def solveActivity(id):
	if session['id']:
		activity = Activity.get_activity_by_id(id)
		datasetId= activity['dataset_id']
		socialGraph = activity['social_graph']

		graphs = Activity.get_graph_of_activity_by_id(id)
		plotterTab = len(graphs) != 0

		return render_template('activities/solve_activity.html', activity=activity, activityId=id, datasetId=datasetId, noNav=True, socialGraph=socialGraph, plotterTab=plotterTab)