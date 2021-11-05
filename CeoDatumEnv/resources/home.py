from flask import redirect, render_template, request, url_for, session, abort, flash, jsonify
from models.home import Home
import os
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from pyspark.sql import SQLContext, Row, SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.sql import types 
from pyspark.sql import functions as F
from pyspark.sql.functions import *
from pyspark.sql import  Window
from pyspark.sql.types import DateType


UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['csv', 'json'])

dictionaryTypes = { 'int' : 'integer',
					'date' : 'date',
					'varchar(255)' : 'string',
					'float' : 'float'
					 }

def dragAndDrop():
	return render_template('home/dragAndDrop.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uploadFile():
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

				firstRow = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename)).first()

				return render_template('home/uploadConfiguration.html', firstRow = firstRow, filename=filename)

			else:

				if fileType == 'json':

					return render_template('home/uploadConfigurationJSON.html', filename=filename)

	else:

		return '4'


def configurateUploadJSON ():

	fileName = request.form['filename']

	database = request.form['database']

	Home.create_database(database)

	databaseInCeoDatum = Home.add_new_database_to_ceoDatum(database)
	
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

	JSONRecursion(database, data, firstRow, sqlContext, spark, objectTable['id'], pos+1, pos, firstRelationName)	

	

def detectType(xString):

	if xString.isdigit():
		return 'int'
	else:
		if xString.replace('.','',1).isdigit() or xString.replace(',','',1).isdigit() :
			return 'float'
		else:

			#HACER
			if xString == 'fecha':
				aa
			else:
				return 'varchar(255)'	



def JSONRecursionStarter(database, data, firstRow, sqlContext, spark, idFactTable, pos):

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

			dfPos = pos

			df.registerTempTable('t'+str(pos))

			dataJoin = data.join(df, None ,'inner')

			for field in dataJoin.first()[x].__fields__:

				dataJoin = dataJoin.filter(x+'[\''+field+'\'] == '+field)

			Home.create_relation_table(database, x)

			dataJoin = dataJoin.select('id', 'id_'+x).withColumnRenamed('id', 'id_'+database)

			dataJoin.write.format("jdbc")\
			    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
			    .option("dbtable", ("\""+database+"-"+x+"\"")) \
			    .option("user", "sebaber12") \
			    .option("password", "sebas") \
			    .option("driver", "org.postgresql.Driver") \
			    .mode("append")\
			    .save()

			objectTable = Home.add_table_and_columns_to_ceoDatum_recursion(x, database, idFactTable)    

			pos = JSONRecursion(database, df, firstRow[x], sqlContext, spark, objectTable['id'], pos+1, pos, x)
    
				
		else:

			if x != 'id':

				xType = detectType(firstRow[x])


				Home.create_table(x, database, xType)

				tableInCeoDatum = Home.add_columns_to_ceoDatum(x, idFactTable, xType)

				table = data.select(x).distinct()

				if xType == 'date':

					table =  table.select(to_date(col(x),"dd/MM/yyyy").alias())

				else:	

					table = table.withColumn(x, table[x].cast(dictionaryTypes[xType]))

				table.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+x+"\"")) \
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

				Home.create_relation_table(database, x)

				relationTable = sqlContext.sql('SELECT factTable.id as id_'+database+', t'+ str(pos) +'.id as id_'+x+' FROM factTable as factTable ' + 'INNER JOIN t'+str(pos)+' as t'+str(pos)+' ON factTable.'+x+' = t'+str(pos)+'.'+x )

				relationTable.write.format("jdbc")\
					.option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
					.option("dbtable", ("\""+database+"-"+x+"\"")) \
					.option("user", "sebaber12") \
			    	.option("password", "sebas") \
			    	.option("driver", "org.postgresql.Driver") \
			    	.mode("append")\
			    	.save()


		pos = pos + 1	

def JSONRecursion(database, data, firstRow, sqlContext, spark, idTable, pos, posObject, objectName):

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

			pos = JSONRecursion(database, df, firstRow[x], sqlContext, spark, objectTable['id'], pos+1, pos, x)    



			"""df = spark.sparkContext.parallelize(list([(row[x]) for row in data.select(x).collect()])).toDF()
									
												pos = JSONRecursion(database, df, firstRow[x], sqlContext, spark, idFactTable, pos, pos, x)"""

				
		else:

			if x != 'id_'+objectName:

				xType = detectType(str(firstRow[x]))


				Home.create_table_recursion('object-'+objectName+'-'+x, database, xType,x)

				tableInCeoDatum = Home.add_columns_to_ceoDatum(x, idTable, xType)

				table = data.select(x).distinct()

				if xType == 'date':

					table =  table.select(to_date(col(x),"dd/MM/yyyy").alias())

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

		if filename.rsplit('.', 1)[1] == 'csv':

			filename = request.form['filename']

			database = request.form['database']

			Home.create_database(database)

			databaseInCeoDatum = Home.add_new_database_to_ceoDatum(database)

			spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
			sqlContext = SQLContext(spark)

			data = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename))

			w = Window.orderBy('id2')
			data = data.withColumn("id2", F.monotonically_increasing_id()).withColumn("id", F.row_number().over(w))    

			data.registerTempTable('factTable')

			factTableInCeoDatum = Home.add_fact_table_ceoDatum(database, databaseInCeoDatum['id'])		

			loop = 1
				
			#creationColumnsFactTable = ''

			#selectPySparkFactTableQuery = ''

			#innerJoinsPysparkFactTableQuery = ''

			while request.form.get('nameColumn'+ str(loop)):

				Home.create_table(request.form.get('nameColumn'+ str(loop)), database, request.form.get('select'+ str(loop)) )

				tableInCeoDatum = Home.add_columns_to_ceoDatum(request.form.get('nameColumn'+ str(loop)), factTableInCeoDatum['id'], request.form.get('select'+ str(loop)))

				#creationColumnsFactTable = creationColumnsFactTable + request.form.get('nameColumn'+ str(loop))+" int NOT NULL, "

				table = data.select("_c"+str(loop-1)).withColumnRenamed(('_c'+str(loop-1)),request.form.get('nameColumn'+ str(loop))).distinct()

				if request.form.get('select'+ str(loop)) == 'date':

					table =  table.select(to_date(col(request.form.get('nameColumn'+ str(loop))),"dd/MM/yyyy").alias(request.form.get('nameColumn'+ str(loop))))

				else:	

					table = table.withColumn(request.form.get('nameColumn'+ str(loop)), table[request.form.get('nameColumn'+ str(loop))].cast(dictionaryTypes[request.form.get('select'+ str(loop))]))

				#selectPySparkFactTableQuery = selectPySparkFactTableQuery + 't'+str(loop)+'.id as ' + request.form.get('nameColumn'+ str(loop)) + ', '

				#innerJoinsPysparkFactTableQuery = innerJoinsPysparkFactTableQuery + 'INNER JOIN t'+str(loop)+' as t'+str(loop)+' ON factTable._c'+str(loop-1)+' = t'+str(loop)+'.'+request.form.get('nameColumn'+ str(loop)) + ' '

				table.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+request.form.get('nameColumn'+ str(loop))+"\"")) \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()

				if request.form.get('select'+ str(loop)) == 'date':
					table = data.select("_c"+str(loop-1)).withColumnRenamed(('_c'+str(loop-1)),request.form.get('nameColumn'+ str(loop))).distinct()
					    

				w = Window.orderBy('id2')
				table = table.withColumn("id2", F.monotonically_increasing_id()).withColumn("id", F.row_number().over(w))    

				table.registerTempTable("t"+str(loop))

				Home.create_relation_table(database, request.form.get('nameColumn'+ str(loop)))

				relationTable = sqlContext.sql('SELECT factTable.id as id_'+database+', t'+ str(loop) +'.id as id_'+request.form.get('nameColumn'+ str(loop))+' FROM factTable as factTable ' + 'INNER JOIN t'+str(loop)+' as t'+str(loop)+' ON factTable._c'+str(loop-1)+' = t'+str(loop)+'.'+request.form.get('nameColumn'+ str(loop)) )

				relationTable.write.format("jdbc")\
					.option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
					.option("dbtable", ("\""+database+"-"+request.form.get('nameColumn'+ str(loop))+"\"")) \
					.option("user", "sebaber12") \
			    	.option("password", "sebas") \
			    	.option("driver", "org.postgresql.Driver") \
			    	.mode("append")\
			    	.save()

				loop = loop + 1

			#fact_table
			Home.create_fact_table(database)	

			factTable = sqlContext.sql(' SELECT factTable.id FROM factTable as factTable ')

			factTable.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+database+"\"")) \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()


			"""creationColumnsFactTable = creationColumnsFactTable[:-2]	

			selectPySparkFactTableQuery = selectPySparkFactTableQuery [:-2]

			#fact_table
			Home.create_fact_table(database, creationColumnsFactTable)	

			factTable = sqlContext.sql(' SELECT ' + selectPySparkFactTableQuery + ' FROM factTable as factTable ' + innerJoinsPysparkFactTableQuery)

			factTable.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
				    .option("dbtable", ("\""+database+"\"")) \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()

			"""

			return '5'

		else:	



			return '4'

	else:

		return '3'
