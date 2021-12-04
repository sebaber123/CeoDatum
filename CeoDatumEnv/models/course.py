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
	def create_course(cls, name, start_date, end_date, owner_id):

		con = get_db()
		query = "INSERT INTO public.course(name, start_date, end_date, id_owner) VALUES(%s, %s, %s, %s)"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (name, start_date, end_date, owner_id))
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
		query = "INSERT INTO public.user_course VALUES(%s, %s)"
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
