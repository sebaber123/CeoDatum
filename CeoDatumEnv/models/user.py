from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class User(object):

	db = None

	@classmethod
	def get_all_users(cls):
		query = "SELECT * FROM public.user"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod
	def login(cls, user, email):
		query= "SELECT * FROM public.user as u INNER JOIN user_role ON user_role.user_id = id INNER JOIN role ON role.id = user_role.role_id WHERE (username=%s OR email=%s)"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user, email))

		return cursor.fetchall()

	@classmethod
	def register(cls, username, password, province, city, institute, email, name, surname, birthday):
		con = get_db()

		query="INSERT INTO public.user(username, password, province_id, city_id, establishment_id, email, name, surname, birthday) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (username, password, province, city, institute, email, name, surname, birthday))
		a = cursor.fetchone()[0]
		query="INSERT INTO public.user_role VALUES(%s, '3')"
		cursor.execute(query, (a,))
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

		query = "SELECT * FROM public.user as u INNER JOIN user_course ON user_course.user_id = u.id ORDER BY surname asc"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (course_id,))

		return cursor.fetchall()

	@classmethod
	def get_roles_of_user(cls, user_id):
		query = "SELECT role_id FROM public.user_role WHERE user_id = %s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user_id,))

		return cursor.fetchall()

	@classmethod
	def user_or_email_exist(cls, username):
		query = "SELECT * FROM public.user WHERE email=%s or username=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (username, username))

		return cursor.fetchone()

	@classmethod
	def get_user_by_id(cls, id_user):
		query = "SELECT * FROM public.user WHERE id=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (id_user,))

		return cursor.fetchone()	


