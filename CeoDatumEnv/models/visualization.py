from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db, get_db_visualization

class Visualization(object):

	db = None

	@classmethod
	def get_data(cls, data_db_name, table, column_x, column_y):
		query = "SELECT " + column_x + ", "+ column_y + " FROM " + table
		cursor = get_db_visualization(data_db_name).cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()
