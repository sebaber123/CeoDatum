from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class Activity(object):

	db = None

	@classmethod
	def getMyActivities(cls, user_id):
		query = "SELECT a.id, a.start_date, a.end_date, title, has_calification, enable_expired_date, calification, commentary, is_finished, name as course_name  FROM public.activity as a INNER JOIN user_activity ON user_activity.id_activity = a.id INNER JOIN course ON a.course_id= course.id WHERE id_user=%s ORDER BY a.end_date desc"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user_id,))
		return cursor.fetchall()

	@classmethod
	def create_activity(cls, start_date, end_date, title, description, course_id, graphs, objective, has_calification, enable_expired_date, statement_title, statement, students, datasetId, socialGraph):
		con = get_db()
		query = "INSERT INTO public.activity(start_date, end_date, title, description, course_id, objective, has_calification, enable_expired_date,statement_title, statement, dataset_id, social_graph) VALUES(%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (start_date, end_date, title, description, course_id, objective, has_calification, enable_expired_date, statement_title, statement, str(datasetId), str(socialGraph)))
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

	@classmethod
	def get_graph_of_activity_by_id(cls, activity_id):
		query = "SELECT * FROM public.activity_available_graph as aag INNER JOIN public.\"Graph\" as g on aag.graph_id = g.id WHERE aag.activity_id=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (str(activity_id),))

		return cursor.fetchall()

	@classmethod
	def get_students_from_activity(cls, activity_id):
		query = "SELECT * FROM public.user u INNER JOIN user_activity ua ON u.id = ua.id_user WHERE ua.id_activity=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (str(activity_id),))

		return cursor.fetchall()

	@classmethod
	def get_activity_of_student(cls,activity_id, user_id):
		query = "SELECT * FROM public.user_activity INNER JOIN public.user u ON u.id = user_activity.id_user WHERE id_activity=%s and id_user=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (activity_id,user_id))

		return cursor.fetchone()

	@classmethod
	def correct_activity(cls, activity_id, user_id, calification, commentary):
		con = get_db()
		query = "UPDATE user_activity SET calification=%s, commentary=%s WHERE id_activity=%s and id_user=%s"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (calification, commentary, activity_id,user_id))
		con.commit()

		return True
