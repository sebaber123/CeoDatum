from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class Activity(object):

	db = None

	@classmethod
	def getActivities(cls, user_id):
		query = "SELECT *  FROM public.activity INNER JOIN user_activity ON user_activity.id_activity=activity.id WHERE user_activity.id_user=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user_id,))

		return cursor.fetchall()

	@classmethod
	def create_activity(cls, start_date, end_date, title, description, course_id, graphs):
		con = get_db()
		query = "INSERT INTO public.activity(start_date, end_date, title, description, course_id) VALUES(%s,%s,%s,%s,%s) RETURNING id;"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (start_date, end_date, title, description, course_id))
		a = cursor.fetchone()[0]
		query = "INSERT INTO public.activity_available_graph VALUES(%s, %s)"
		var = []
		for graph in graphs:
			var.append((a,graph))
		cursor.executemany(query, var)
		con.commit()
		
		return 

	@classmethod 
	def get_graph_names(cls):
		query = "SELECT id, spanish_name FROM graph"
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
