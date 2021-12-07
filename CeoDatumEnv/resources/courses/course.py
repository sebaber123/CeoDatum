from flask import redirect, jsonify, render_template, request, url_for, session, abort, flash
from db import get_db
from models.course import Course
from models.activity import Activity
from models.dataset import Dataset
from models.user import User
from datetime import date

def get_courses():
	if session['role']=="professor":
		cursos = Course.get_my_courses(session['id'])
		return render_template('course/courses.html', cursos=cursos)
	else:
		return redirect(url_for('home'))

def new_course():
	if session['role']=="professor" :
		return render_template('course/new_course.html')
	else:
		return redirect(url_for('home'))

def create_course():
	if request.method=="POST":
		nombre = request.form['name']
		fecha_comienzo = request.form['startDate']
		fecha_fin = request.form['endDate']

		establismentId = (User.get_user_by_id(session['id']))['establishment_id']

		Course.create_course(nombre, fecha_comienzo, fecha_fin, session['user_id'], establismentId)
		return redirect(url_for('courses'))
	return redirect(url_for('home'))

def view_course(course_id):
	if session['role']=="professor":
		course = Course.get_course(course_id)
		activities = Activity.get_activities_of_course(course_id)
		students = User.get_user_from_course(course_id)

		establismentId = (User.get_user_by_id(session['id']))['establishment_id']

		datasetsToAdd = Dataset.get_datasets_to_add_to_course(session['id'], establismentId, course_id)

		datasets = Course.get_dataset_by_courseId(course_id)

		return render_template('course/view_course.html', course=course, activities=activities, fecha_actual=date.today(), alumnos=students, datasetsToAdd=datasetsToAdd, datasets=datasets)
	return redirect(url_for('home'))

def invite_user_to_course(username, course_id):
	if session['role']=="professor":
		result = Course.invite_user_to_course(username,course_id)
		return jsonify(result = result)

def is_user_on_course(username, course_id):
	if session['role']=="professor":
		result = Course.is_user_on_course(username,course_id)
		return jsonify(result = result)

def course_add_dataset():
	if request.method=="POST":
		datasetId = request.form['dataset']
		courseId = request.form['courseId']

		Course.add_dataset(datasetId, courseId)

		return view_course(courseId)

