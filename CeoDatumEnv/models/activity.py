from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class Activity(object):

	db = None

	@classmethod
	def getMyActivities(cls, user_id):
		query = "SELECT * FROM public.activity as a INNER JOIN user_activity ON user_activity.id_activity = a.id WHERE id_user=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user_id,))
		return cursor.fetchall()

	@classmethod
	def create_activity(cls, start_date, end_date, title, description, course_id, graphs, objective, has_calification, enable_expired_date, statement_title, statement, students):
		con = get_db()
		query = "INSERT INTO public.activity(start_date, end_date, title, description, course_id, objective, has_calification, enable_expired_date,statement_title, statement) VALUES(%s,%s,%s,%s,%s, %s, %s, %s, %s, %s) RETURNING id;"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (start_date, end_date, title, description, course_id, objective, has_calification, enable_expired_date, statement_title, statement))
		a = cursor.fetchone()[0]
		query = "INSERT INTO public.activity_available_graph VALUES(%s, %s)"
		var = []
		for graph in graphs:
			var.append((a,graph))
		cursor.executemany(query, var)
		query3 = "INSERT INTO public.user_activity(id_user, id_activity) VALUES(%s, %s)"
		var2 = []
		for student in students:
			var2.append((student, a))
		cursor.executemany(query3, var2)
		con.commit()
		return True


	@classmethod 
	def get_graph_names(cls):
		query = "SELECT id, spanish_name FROM public.\"Graph\""
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod
	def get_activities_of_course(cls, course_id):
		query = "SELECT * FROM activity WHERE course_id=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (course_id,))

		return cursor.fetchall()

	@classmethod
	def get_activity_by_id(cls, activity_id):
		query = "SELECT * FROM activity WHERE id=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (activity_id,))

		return cursor.fetchone()
