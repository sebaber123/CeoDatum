from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db, get_db_visualization

class Visualization(object):

	db = None

	@classmethod
	def get_database(cls, Bid):
		query = ("SELECT * FROM public.\"Database\" as d " +
				"WHERE d.id = %s")
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query,(str(Bid)))

		return cursor.fetchone()

	@classmethod
	def get_db_data(cls, Bid):
		query = ("SELECT C.name, C.type FROM public.\"Database\" as d inner join public.\"Database_table\" as dt on d.id = dt.id_database " +
				"inner join public.\"Table\" as t on dt.id_table = t.id " +
				"inner join public.\"Table_column\" as tc on t.id = tc.id_table " +
				"inner join public.\"Column\" as c on tc.id_column = c.id " +
				"WHERE t.fact_table = True AND d.id = %s")
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query,(str(Bid)))

		return cursor.fetchall()


	@classmethod
	def get_data(cls, data_db_name, table, column_x, condition, innerColumnsCondition):
		query = ("SELECT t0." +column_x + ", COUNT(t.id) as count " +
				" FROM \"" + table + "\" as t INNER JOIN " + "\""+ table + "-" + column_x + "\" as t0 on (t." + column_x + " = t0.id )" + innerColumnsCondition + " " +
				condition + 
				" GROUP BY t0." + column_x +" ORDER BY " + column_x + " ASC ")
		cursor = get_db_visualization(data_db_name).cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod
	def getColumnData(cls, database, column):
		query = ("SELECT * FROM \"" + database + "-" + column + "\"")
		cursor = get_db_visualization(database).cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod	
	def get_data_for_data_table(cls, data_db_name, row, column, condition, innerColumnsCondition, counts):
		query = ("SELECT t0." +row + ", "+ counts +
				" FROM \"" + data_db_name + "\" as t INNER JOIN " + "\""+ data_db_name + "-" + row + "\" as t0 on (t." + row + " = t0.id ) " + 
				"INNER JOIN \""+ data_db_name + "-" + column + "\" as t1 on (t."+column+" = t1.id) "+
				innerColumnsCondition + " " +
				condition + 
				" GROUP BY t0." + row +" ORDER BY " + row + " ASC ")
		cursor = get_db_visualization(data_db_name).cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()	



