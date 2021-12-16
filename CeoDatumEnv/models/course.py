from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class Course(object):

	db = None

	@classmethod
	def get_my_courses(cls, user_id):
		query = "SELECT *  FROM public.course WHERE id_owner=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user_id,))

		return cursor.fetchall()

	@classmethod	
	def create_course(cls, name, start_date, end_date, owner_id, establishment_id):

		con = get_db()
		query = "INSERT INTO public.course(name, start_date, end_date, id_owner, id_establishment) VALUES(%s, %s, %s, %s, %s)"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (name, start_date, end_date, owner_id, str(establishment_id)))
		con.commit()

		return True

	@classmethod
	def get_course(cls, id_course):
		query = "SELECT * FROM public.course WHERE id=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (id_course,))
		return cursor.fetchone()

	@classmethod
	def invite_user_to_course(cls,username,course_id):

		con = get_db()
		query = "INSERT INTO public.user_course(user_id, course_id) VALUES(%s, %s)"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (username,course_id))
		con.commit()
		query = "SELECT * FROM public.user WHERE id=%s"
		cursor.execute(query, (username,))

		return cursor.fetchone()

	@classmethod
	def is_user_on_course(cls,username,course_id):
		query = "SELECT * FROM public.user_course WHERE user_id=%s and course_id=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (username,course_id))
		if cursor.fetchone():
			return True
		return False

	@classmethod
	def add_dataset(cls, dataset_id, course_id):	

		con = get_db()
		query = "INSERT INTO public.\"Dataset_course\"(id_dataset, id_course) VALUES(%s, %s)"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (str(dataset_id), str(course_id)))
		con.commit()

		return None

	@classmethod
	def get_dataset_by_courseId(cls, course_id):

		query = ("SELECT d.id, d.name as dataset_name, u.name, u.surname FROM public.\"Database\" as d "+ 
				"INNER JOIN public.\"user\" as u on d.database_owner_id = u.id " + 
				"INNER JOIN public.\"Dataset_course\" as dc on dc.id_dataset = d.id "+
				"WHERE dc.id_course = "+str(course_id)  )

		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()	