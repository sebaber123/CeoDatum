from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.course import Course

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
		Course.create_course(nombre, fecha_comienzo, fecha_fin, session['id'])
		return redirect(url_for('courses'))
	return redirect(url_for('home'))

def view_course(course_id):
	if session['role']=="professor":
		course = Course.get_course(course_id)
		return render_template('course/view_course.html', curso=course)
	return redirect(url_for('home'))
