from flask import redirect, jsonify, render_template, request, url_for, session, abort, flash
from db import get_db
from models.course import Course
from models.activity import Activity
from models.dataset import Dataset
from models.user import User
from datetime import date
import datetime

def get_courses():
	if session['actualRole'] == "professor":
		cursos = Course.get_my_courses(session['id'])
		return render_template('course/courses.html', cursos=cursos)
	else:
		return redirect(url_for('home'))

def new_course():
	if session['actualRole'] == "professor":
		curricularScopes = get_curricular_scope()
		return render_template('course/new_course.html', curricularScopes=curricularScopes)
	else:
		return redirect(url_for('home'))

def create_course():
	if request.method=="POST":
		if 'name' in request.form and 'startDate' in request.form and 'endDate' in request.form:
			nombre = request.form['name']
			fecha_comienzo = request.form['startDate']
			fecha_fin = request.form['endDate']
			establismentId = (User.get_user_by_id(session['id']))['establishment_id']
			cicle = request.form['inputCiclo']
			if cicle and cicle=='1':
				year = request.form['inputAnioBasico']
			elif cicle=='2':
				year = request.form['inputAnioSuperior']
			curricular_scope = request.form['inputCurricularScope']
			if not(nombre=="" or fecha_comienzo=="" or fecha_fin=="" or cicle=="" or curricular_scope ==""):
				fecha_comienzo = datetime.datetime.strptime(fecha_comienzo, '%Y-%m-%d')
				fecha_fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
				if fecha_fin<fecha_comienzo:
					render_template('course/new_course.html', dateError="La fecha de comienzo debe ser anterior a la de fin.")
				hoy = datetime.datetime.strptime(str(date.today()), '%Y-%m-%d')
				if fecha_comienzo<hoy:
					render_template('course/new_course.html', dateError="La fecha de comienzo debe ser posterior a la fecha actual.")
				Course.create_course(nombre, fecha_comienzo, fecha_fin, session['id'], establismentId, cicle, year, curricular_scope)
				return redirect(url_for('courses'))
		curricularScopes = get_curricular_scope()
		return render_template('course/new_course.html', curricularScopes=curricularScopes)
		return render_template('course/new_course.html', emptyField="Debe completar todos los campos.")
	return redirect(url_for('home'))

def view_course(course_id):
	if session['actualRole'] == "professor":
		course = Course.get_course(course_id)
		
		activities = Activity.get_activities_of_course(course_id)
		students = User.get_user_from_course(course_id)
		

		establismentId = (User.get_user_by_id(session['id']))['establishment_id']

		datasetsToAdd = Dataset.get_datasets_to_add_to_course(session['id'], establismentId, course_id)

		datasets = Course.get_dataset_by_courseId(course_id)

		return render_template('course/view_course.html', course=course, activities=activities, fecha_actual=date.today(), alumnos=students, datasetsToAdd=datasetsToAdd, datasets=datasets)
	return redirect(url_for('home'))

def invite_user_to_course(username, course_id):
	if session['actualRole'] == "professor":
		result = Course.invite_user_to_course(username,course_id)
		return jsonify(result = result)
	return redirect(url_for('home'))


def is_user_on_course(username, course_id):
	if session['actualRole'] == "professor":
		result = Course.is_user_on_course(username,course_id)
		return jsonify(result = result)
	return redirect(url_for('home'))

def course_add_dataset():
	if request.method=="POST":
		datasetId = request.form['dataset']
		courseId = request.form['courseId']

		Course.add_dataset(datasetId, courseId)

		return view_course(courseId)
	return redirect(url_for('home'))

def get_curricular_scope():
	if session['actualRole'] == "professor":
		curricularScopes = Course.get_curricular_scope()
		return curricularScopes
	return redirect(url_for('home'))
