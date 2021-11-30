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