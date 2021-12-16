from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.activity import Activity
from models.course import Course
from models.user import User
from datetime import date


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
		alumnos = Activity.get_students_from_activity(id)
		return render_template('activities/activity_view_data.html', activity=actividad, available_graphs=graficos_disponibles, students=alumnos)

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

def correct_activity_view(activity_id, user_id):
	if session['id']:
		activity = Activity.get_activity_by_id(activity_id)
		alumno = Activity.get_activity_of_student(activity_id, user_id)
		return render_template('activities/correct_activity.html', activity=activity, student=alumno)

def correct_activity(activity_id, user_id):
	if request.method=="POST":
		comentario = request.form['comment']
		nota = 'calification' in request.form
		if not nota:
			nota = -1
		Activity.correct_activity(activity_id, user_id, nota, comentario)
		return redirect(url_for('courses'))
	return redirect(url_for('home'))