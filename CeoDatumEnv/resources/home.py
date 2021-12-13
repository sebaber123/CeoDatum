from flask import redirect, render_template, request, url_for, session, abort, flash, jsonify
from models.home import Home
from models.user import User
import os
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from pyspark.sql import SQLContext, Row, SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.sql import types 
from pyspark.sql import functions as F
from pyspark.sql import types as T
from pyspark.sql.functions import *
from pyspark.sql import  Window
from pyspark.sql.types import DateType, TimestampType, DoubleType


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['csv', 'json'])

dictionaryTypes = { 'int' : 'integer',
					'date' : 'date',
					'varchar(255)' : 'string',
					'NUMERIC (16, 10)' : DoubleType(),
					'TIMESTAMP' : TimestampType()

					 }

def dragAndDrop():
	if session:

		return render_template('home/dragAndDrop.html')
	
	else:

		return redirect(url_for('loginForm'))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uploadFile():

	if session:

		if request.method == 'POST':
			
			file = request.files['file']

			filename = secure_filename(file.filename)
			
			if file and allowed_file(filename):

				filename = secure_filename(filename)
				file.save(os.path.join(UPLOAD_FOLDER, filename))

				fileType = filename.rsplit('.', 1)[1]

				if fileType == 'csv':

					spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
					sqlContext = SQLContext(spark)

					firstRow = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename)).limit(2).first()

					return render_template('home/uploadConfiguration.html', firstRow = firstRow, filename=filename)

				else:

					if fileType == 'json':

						return render_template('home/uploadConfigurationJSON.html', filename=filename)

					else: 
						flash('Debe subir un archivo de tipo CSV o JSON', 'danger')

						return render_template('home/dragAndDrop.html')

		else:

			return '4'

	else:

		flash('Debe estar logueado para usar esta funcion.', 'danger')

		return render_template('home/dragAndDrop.html')		


def configurateUploadJSON ():

	sessionId= session['id']

	fileName = request.form['filename']

	database = request.form['database']

	database = database.replace(' ','_').replace('.','')

	share = request.form['share']

	aa

	dateFormat =  request.form['dateFormat']

	try:

		Home.create_database(database)

		databaseInCeoDatum = Home.add_new_database_to_ceoDatum(database, str(sessionId), share)

		if share == 'protegido':

			establismentId = (User.get_user_by_id(sessionId))['establishment_id']

			Home.add_dataset_stablishment(databaseInCeoDatum['id'], establismentId)
		
		spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
		sqlContext = SQLContext(spark)

		#data = sqlContext.read.json(os.path.join(UPLOAD_FOLDER,filename))

		#data = sqlContext.read.format('org.apache.spark.sql.json').load(os.path.join(UPLOAD_FOLDER,filename))
		
		data = sqlContext.read.option("multiline", "true").json(os.path.join(UPLOAD_FOLDER,fileName))

		firstRelationName = data.first().__fields__[0]

		data = data.first()[data.first().__fields__[0]]

		data = spark.sparkContext.parallelize(list(data)).toDF()

		w = Window.orderBy('id2')
		data = data.withColumn("id2", F.monotonically_increasing_id()).withColumn("id_"+firstRelationName, F.row_number().over(w))   

		data = data.drop('id2') 

		data.registerTempTable('factTable')

		factTableInCeoDatum = Home.add_fact_table_ceoDatum(database, databaseInCeoDatum['id'])

		pos = 0

		firstRow = data.first()

		firstRowFields = firstRow.__fields__

		Home.create_fact_table(database)	

		factTable = sqlContext.sql(' SELECT factTable.id_'+firstRelationName+' as id FROM factTable as factTable ')

		factTable.write.format("jdbc")\
			    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
			    .option("dbtable", ("\""+database+"\"")) \
			    .option("user", "sebaber12") \
			    .option("password", "sebas") \
			    .option("driver", "org.postgresql.Driver") \
			    .mode("append")\
			    .save()

		Home.create_relation_table(database, firstRelationName)	 

		data.registerTempTable('t'+str(pos))

		df = sqlContext.sql(' SELECT factTable.id_'+firstRelationName+' as id_'+database+', factTable.id_'+firstRelationName+' as id_'+firstRelationName+' FROM factTable as factTable ')   

		df.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+database+"-"+firstRelationName+"\"")) \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()

		objectTable = Home.add_table_and_columns_to_ceoDatum_recursion(firstRelationName, database, factTableInCeoDatum['id'])    

		JSONRecursion(database, data, firstRow, sqlContext, spark, objectTable['id'], pos+1, pos, firstRelationName, dateFormat)	

		flash('Dataset cargado correctamente', 'info')

		return render_template('home/dragAndDrop.html')		


	except BaseException as e:

		exceptionString = str(e)

		if 'database \"'+database+'\" already exists' in exceptionString:

			flash('Ya hay un dataset con ese nombre. Debe escribir otro nombre.', 'danger')

			return render_template('home/uploadConfigurationJSON.html', filename=fileName)

		else:

			Home.delete_dataset(database)

			if 'wrong format of date in field' in exceptionString:

				flash('El campo '+ exceptionString.replace('wrong format of date in field ','')+ ' tiene otro formato de fecha' , 'danger')

				return render_template('home/uploadConfigurationJSON.html', filename=fileName)
			
			flash('Lo sentimos, la carga del dataset ha fallado', 'danger')

			return render_template('home/dragAndDrop.html')



def detectType(xString):

	if xString.isdigit():
		return 'int'
	else:
		if xString.replace('.','',1).isdigit():
			return 'NUMERIC (16, 10)'
		else:

			if xString.replace('/','').replace('-','').isdigit():
				return 'date'

			else:	

				#HACER
				if xString.replace('/','').replace('-','').replace(':','').replace('.','').replace(' ','').isdigit():
					return 'TIMESTAMP'
				
				else:

					return 'varchar(255)'


def JSONRecursion(database, data, firstRow, sqlContext, spark, idTable, pos, posObject, objectName, dateFormat):

	firstRowFields = firstRow.__fields__
	
	for x in firstRowFields:

		if str(type(firstRow[x])) == "<class 'list'>":

			data = data.withColumn(x, explode(x))
			
			firstRow = sqlContext.createDataFrame([firstRow]).withColumn(x, explode(x)).first()

		if str(type(firstRow[x])) == "<class 'pyspark.sql.types.Row'>":

			df = spark.sparkContext.parallelize(list([(row[x]) for row in data.select(x).distinct().collect()])).toDF()

			w = Window.orderBy('id2')
			df = df.withColumn("id2", F.monotonically_increasing_id()).withColumn("id_"+x, F.row_number().over(w))   

			df = df.drop('id2') 

			df.registerTempTable('t'+str(pos))

			dataJoin = data.join(df, None ,'inner')

			for field in dataJoin.first()[x].__fields__:

				dataJoin = dataJoin.filter(x+'[\''+field+'\'] == '+field)

			Home.create_relation_table_recursion(database, x, objectName)

			dataJoin = dataJoin.select('id_'+objectName, 'id_'+x)

			dataJoin.write.format("jdbc")\
			    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
			    .option("dbtable", ("\""+objectName+"-"+x+"\"")) \
			    .option("user", "sebaber12") \
			    .option("password", "sebas") \
			    .option("driver", "org.postgresql.Driver") \
			    .mode("append")\
			    .save()

			objectTable = Home.add_table_and_columns_to_ceoDatum_recursion(x, database+'-'+objectName, idTable)    

			pos = JSONRecursion(database, df, firstRow[x], sqlContext, spark, objectTable['id'], pos+1, pos, x, dateFormat)    



			"""df = spark.sparkContext.parallelize(list([(row[x]) for row in data.select(x).collect()])).toDF()
									
												pos = JSONRecursion(database, df, firstRow[x], sqlContext, spark, idFactTable, pos, pos, x)"""

				
		else:

			if x != 'id_'+objectName:

				xType = detectType(str(firstRow[x]))


				Home.create_table_recursion('object-'+objectName+'-'+x, database, xType,x)

				tableInCeoDatum = Home.add_columns_to_ceoDatum(x, idTable, xType)

				table = data.select(x).distinct()

				if xType == 'date':

					tableToCompare = table

					table =  table.select(to_date(col(x),dateFormat).alias(x))

					if (tableToCompare.first()[0] != None) and (table.first()[0] == None):

						raise Exception('wrong format of date in field ' + x)


				else:
					
					if xType == 'TIMESTAMP':

						tableToCompare = table
							
						table = table.select(to_timestamp(col(x),dateFormat+' HH:mm:ss.SSSS')).alias(x)

						if (tableToCompare.first()[0] != None) and (table.first()[0] == None):

							raise Exception('wrong format of date in field ' + x)	

					else:	

						table = table.withColumn(x, table[x].cast(dictionaryTypes[xType]))

				table.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+'object-'+objectName+'-'+x+"\"")) \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()

				if xType == 'date':
					table = data.select(x).distinct()
					    

				w = Window.orderBy('id2')
				table = table.withColumn("id2", F.monotonically_increasing_id()).withColumn("id", F.row_number().over(w))

				table.registerTempTable("t"+str(pos))

				Home.create_relation_table_recursion(database, x, objectName)

				relationTable = sqlContext.sql('SELECT factTable.id_'+objectName+' as id_'+objectName+', t'+ str(pos) +'.id as id_'+x+' FROM t'+str(posObject)+' as factTable ' + 'INNER JOIN t'+str(pos)+' as t'+str(pos)+' ON factTable.'+x+' = t'+str(pos)+'.'+x )

				relationTable.write.format("jdbc")\
					.option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
					.option("dbtable", ("\""+objectName+"-"+x+"\"")) \
					.option("user", "sebaber12") \
			    	.option("password", "sebas") \
			    	.option("driver", "org.postgresql.Driver") \
			    	.mode("append")\
			    	.save()


		pos = pos + 1			

	return pos	



def configurateUploadCSV():
	if request.method == 'POST':

		sessionId= session['id']

		filename = request.form['filename']

		database = request.form['database']

		database = database.replace(' ','_').replace('.','')

		share = request.form['share']

		dateFormat =  request.form['dateFormat']

		try:

			Home.create_database(database)

			databaseInCeoDatum = Home.add_new_database_to_ceoDatum(database, str(sessionId), share)

			if share == 'protegido':

				establismentId = (User.get_user_by_id(sessionId))['establishment_id']

				Home.add_dataset_stablishment(databaseInCeoDatum['id'], establismentId)

			spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
			sqlContext = SQLContext(spark)

			data = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename))

			loop = 1

			while request.form.get('nameColumn'+ str(loop)):

				data = data.withColumnRenamed('_c'+str(loop-1), (request.form.get('nameColumn'+ str(loop))).replace(' ','_').replace('.','') )

				loop = loop + 1

			w = Window.orderBy('id2')
			data = data.withColumn("id2", F.monotonically_increasing_id()).withColumn("id_"+database, F.row_number().over(w))    

			data = data.drop('id2') 


			if request.form['headers'] == 'si':
				data = data.filter(data['id_'+database] != 1)

			data.registerTempTable('t0')

			factTableInCeoDatum = Home.add_fact_table_ceoDatum(database, databaseInCeoDatum['id'])		

			firstRow = data.first()

			firstRowFields = firstRow.__fields__

			idTable = factTableInCeoDatum['id']

			JSONRecursion(database, data, firstRow, sqlContext, spark, factTableInCeoDatum['id'], 1, 0, database, dateFormat)	

			#fact_table
			Home.create_fact_table(database)	

			factTable = sqlContext.sql(' SELECT factTable.id_'+database+' as id FROM t0 as factTable ')

			factTable.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+database+"\"")) \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()


			flash('Dataset cargado correctamente', 'info')

			return render_template('home/dragAndDrop.html')		


		except BaseException as e:

			exceptionString = str(e)

			if 'database \"'+database+'\" already exists' in exceptionString:

				flash('Ya hay un dataset con ese nombre. Debe escribir otro nombre.', 'danger')

				return render_template('home/uploadConfigurationJSON.html', filename=fileName)

			else: 

				Home.delete_dataset(database)

				if 'wrong format of date in field' in exceptionString:

					flash('El campo '+ exceptionString.replace('wrong format of date in field ','')+ ' tiene otro formato de fecha' , 'danger')

					return render_template('home/uploadConfiguration.html', filename=fileName)
				
				flash('Lo sentimos, la carga del dataset ha fallado', 'danger')

				return render_template('home/dragAndDrop.html')
			
		

	else:

		return '3'
