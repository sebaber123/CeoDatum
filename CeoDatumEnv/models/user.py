from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class User(object):

	db = None

	@classmethod
	def get_all_users(cls):
		query = "SELECT * FROM public.user WHERE role_id != '1'"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod
	def login(cls, user, email):
		query= "SELECT * FROM public.user as u INNER JOIN role ON role.id = u.role_id WHERE (username=%s OR email=%s)"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user, email))

		return cursor.fetchone()

	@classmethod
	def register(cls, username, password, province, city, institute, email, name, surname, birthday):
		con = get_db()

		query="INSERT INTO public.user(username, password, province_id, city_id, establishment_id, email, name, surname, birthday) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (username, password, province, city, institute, email, name, surname, birthday))
		con.commit()

		return True
	

	@classmethod
	def emailExist(cls, email):

		query = "SELECT * FROM public.user WHERE email=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (email,))

		if cursor.fetchone():
			return True
		else: 
			return False

	@classmethod
	def get_user_from_course(cls, course_id):

		query = "SELECT * FROM public.user INNER JOIN user_course ON user_course.user_id = id ORDER BY surname asc"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (course_id,))

		return cursor.fetchall()

	@classmethod
	def user_or_email_exist(cls, username):
		query = "SELECT * FROM public.user WHERE email=%s or username=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (username, username))

		return cursor.fetchone()
