from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db, get_db_visualization
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import config

class Home(object):

	db = None

	@classmethod
	def create_database(cls, databaseName):
		

		con = get_db()

		con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)


		query = ("CREATE DATABASE \""+databaseName+ "\" ;")
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		con.commit()

		return None

	@classmethod
	def create_table(cls, tableName , databaseName, dataType):
		

		con2 = get_db_visualization(databaseName)

		query = ("CREATE TABLE \""+tableName+"\" (ID int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, \""+tableName+"\" "+dataType+" NOT NULL);")
		cursor = con2.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con2.commit()

		return None	

	@classmethod
	def add_new_database_to_ceoDatum(cls, databaseName):
		

		con = get_db()

		query = ("INSERT INTO public.\"Database\" (name) VALUES (\'"+databaseName+"\' )")
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		con.commit()

		query = ("SELECT * FROM public.\"Database\" as d " + "WHERE d.name = \'"+databaseName+"\'")
		cursor.execute(query)

		return cursor.fetchone()

	@classmethod
	def add_fact_table_ceoDatum(cls, databaseName, databaseId):

		con = get_db()

		query = ("INSERT INTO public.\"Table\" (name, fact_table) VALUES (\'"+databaseName+"\', "+'True'+" )")
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con.commit()


		query = ("SELECT * FROM public.\"Table\" as t " + "WHERE t.name = \'"+databaseName+"\'")
		cursor.execute(query)	

		table = cursor.fetchone()

		query = ("INSERT INTO public.\"Database_table\" (id_database, id_table) VALUES ("+str(databaseId)+", "+str(table['id'])+" )")
		cursor.execute(query)
		con.commit()		

		return table


	@classmethod
	def add_columns_to_ceoDatum(cls, tableName, tableId, columnType):
		

		con = get_db()

		query = ("INSERT INTO public.\"Column\" (name, type) VALUES (\'"+tableName+"\', \'"+columnType+"\' ); ")
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		
		con.commit()

		query = ("SELECT * FROM public.\"Column\" as c ORDER BY id DESC LIMIT 1 ;")
		cursor.execute(query)

		column = cursor.fetchone()

		query = ("INSERT INTO public.\"Table_column\" (id_table, id_column) VALUES ("+str(tableId)+", "+str(column['id'])+" )")
		cursor.execute(query)
		con.commit()



		return True

	@classmethod
	def create_fact_table(cls, databaseName):
		

		con2 = get_db_visualization(databaseName)

		query = ("CREATE TABLE \""+databaseName+"\" (ID int NOT NULL);")
		cursor = con2.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con2.commit()

		return None	


	@classmethod
	def create_relation_table(cls, databaseName, tableName):
		

		con2 = get_db_visualization(databaseName)

		query = ("CREATE TABLE \""+databaseName+'-'+tableName + "\" (id_"+databaseName+" int NOT NULL, id_"+tableName+" int NOT NULL);")
		cursor = con2.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con2.commit()

		return None			

	@classmethod
	def create_relation_table_recursion(cls, databaseName, tableName, objectName):
		

		con2 = get_db_visualization(databaseName)

		query = ("CREATE TABLE \""+objectName+'-'+tableName + "\" (id_"+objectName+" int NOT NULL, id_"+tableName+" int NOT NULL);")
		cursor = con2.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con2.commit()

		return None	

	@classmethod
	def create_table_recursion(cls, tableName , databaseName, dataType, columnName):
		

		con2 = get_db_visualization(databaseName)

		query = ("CREATE TABLE \""+tableName+"\" (ID int GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY, \""+columnName+"\" "+dataType+" );")
		cursor = con2.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con2.commit()

		return None	

	@classmethod
	def add_table_and_columns_to_ceoDatum_recursion(cls, tableName, objectName, tableId):
		
		con = get_db()

		query = ("INSERT INTO public.\"Table\" (name, fact_table) VALUES (\'"+objectName+"-"+tableName+"\', "+'False'+" )")
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		con.commit()


		query = ("SELECT * FROM public.\"Table\" as t " + "WHERE t.name = \'"+objectName+"-"+tableName+"\'")
		cursor.execute(query)	

		table = cursor.fetchone()

		con = get_db()

		query = ("INSERT INTO public.\"Column\" (name, type) VALUES (\'"+tableName+"\', \'object\' ); ")
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)
		
		con.commit()

		query = ("SELECT * FROM public.\"Column\" as c ORDER BY id DESC LIMIT 1 ;")
		cursor.execute(query)

		column = cursor.fetchone()

		query = ("INSERT INTO public.\"Table_column\" (id_table, id_column) VALUES ("+str(tableId)+", "+str(column['id'])+" )")
		cursor.execute(query)
		con.commit()	

		return table
	
