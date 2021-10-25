from flask import redirect, render_template, request, url_for, session, abort, flash
import psycopg2
import psycopg2.extras
from db import get_db

class User(object):

	db = None

	@classmethod
	def get_all_users(cls):
		query = "SELECT *  FROM public.user"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod
	def login(cls, user, password):
		query= "SELECT * FROM public.user WHERE name=%s AND password=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (user, password))

		return cursor.fetchone()

	@classmethod
	def register(cls, name, password, email):
		con = get_db()

		query="INSERT INTO public.user(name, password, email) VALUES(%s, %s, %s)"
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (name, password, email))
		con.commit()

		return True
	

	@classmethod
	def emailExist(cls, email):

		query = "SELECT * FROM public.user WHERE email=%s"
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query, (email,))

		if cursor.fetchone():
			return True
		else: 
			return False