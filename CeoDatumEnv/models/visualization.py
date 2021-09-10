from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db, get_db_visualization

class Visualization(object):

	db = None

	@classmethod
	def get_db_data(cls, Bid):
		query = ("SELECT C.name FROM public.\"Database\" as d inner join public.\"Database_table\" as dt on d.id = dt.id_database " +
				"inner join public.\"Table\" as t on dt.id_table = t.id " +
				"inner join public.\"Table_column\" as tc on t.id = tc.id_table " +
				"inner join public.\"Column\" as c on tc.id_column = c.id " +
				"WHERE t.fact_table = True AND d.id = %s")
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query,(str(Bid)))

		return cursor.fetchall()


	@classmethod
	def get_data(cls, data_db_name, table, column_x, condition):
		query = "SELECT " + column_x + ", COUNT(id) as count FROM " + table + condition + " GROUP BY " + column_x +" ORDER BY " + column_x + " ASC "
		cursor = get_db_visualization(data_db_name).cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()
