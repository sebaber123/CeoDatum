import psycopg2
import psycopg2.extras
from db import get_db

class Dataset(object):

	db = None

	@classmethod
	def get_dataset_public(cls, page, pagination):
		start_at = (page-1)*pagination

		query = ("SELECT d.id, d.name as dataset_name, u.name, u.surname FROM public.\"Database\" as d  INNER JOIN public.\"user\" as u on d.database_owner_id = u.id " + 
				"WHERE d.share = 'publico' ORDER BY d.id limit "+str(pagination)+ " OFFSET " +str(start_at)  )

		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchall()

	@classmethod
	def get_dataset(cls, Bid):
		query = ("SELECT * FROM public.\"Database\" as d " +
				"WHERE d.id = "+str(Bid))
		cursor = get_db().cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		return cursor.fetchone()	

	@classmethod
	def dataset_edit_share(cls, Bid, share):
		
		con = get_db()

		query = ("UPDATE public.\"Database\" SET share = '"+ share +
				"' WHERE id = "+str(Bid))
		cursor = con.cursor(cursor_factory = psycopg2.extras.DictCursor)
		cursor.execute(query)

		con.commit()

		return None		