from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.activity import Activity
from models.course import Course
from datetime import date


def activities():
	if session['name']:
		activities = Activity.getActivitiesOfCourses(session['id'])
		return render_template('activities/activities.html', activities=activities, today=date.today())
	else:
		return render_template('/')

def new_activity(course_id):
	if session['role']=='professor':
		graficos = Activity.get_graph_names()

		datasets = datasets = Course.get_dataset_by_courseId(course_id)

		return render_template('activities/new_activity.html', course_id=course_id, graphs=graficos, datasets=datasets)
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
		Activity.create_activity(fecha_comienzo, fecha_fin, titulo, descripcion, curso, graphs)
		return redirect(url_for('courses'))
	return redirect(url_for('home'))

def view_activity(id):
	if session['id']:
		actividad = Activity.get_activity_by_id(id)
		return render_template('activities/activity_view.html', activity=actividad)

