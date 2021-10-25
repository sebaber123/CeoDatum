from flask import redirect, render_template, request, url_for, session, abort, flash, jsonify
from models.home import Home
import os
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from pyspark.sql import SQLContext, Row, SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.sql import types 
from pyspark.sql import functions as F
from pyspark.sql import  Window

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['csv', 'json'])

dictionaryTypes = { 'int' : 'integer',
					'date' : 'date',
					'varchar(255)' : 'string'
					 }

def dragAndDrop():
	return render_template('home/dragAndDrop.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def uploadFile():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
            sqlContext = SQLContext(spark)

            firstRow = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename)).first()

            return render_template('home/uploadConfiguration.html', firstRow = firstRow, filename=filename)

        else:
        	return '4'    

def configurateUpload():
	if request.method == 'POST':

		filename = request.form['filename']

		database = request.form['database']

		Home.create_database(database)

		databaseInCeoDatum = Home.add_new_database_to_ceoDatum(database)

		spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
		sqlContext = SQLContext(spark)

		data = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename))

		data.registerTempTable('factTable')

		factTableInCeoDatum = Home.add_fact_table_ceoDatum(database, databaseInCeoDatum['id'])			

		loop = 1
			
		creationColumnsFactTable = ''

		selectPySparkFactTableQuery = ''

		innerJoinsPysparkFactTableQuery = ''

		while request.form.get('nameColumn'+ str(loop)):

			Home.create_table(request.form.get('nameColumn'+ str(loop)), database, request.form.get('select'+ str(loop)) )

			tableInCeoDatum = Home.add_columns_to_ceoDatum(request.form.get('nameColumn'+ str(loop)), factTableInCeoDatum['id'], request.form.get('select'+ str(loop)))

			creationColumnsFactTable = creationColumnsFactTable + request.form.get('nameColumn'+ str(loop))+" int NOT NULL, "

			table = data.select("_c"+str(loop-1)).withColumnRenamed(('_c'+str(loop-1)),request.form.get('nameColumn'+ str(loop))).distinct()

			table = table.withColumn(request.form.get('nameColumn'+ str(loop)), table[request.form.get('nameColumn'+ str(loop))].cast(dictionaryTypes[request.form.get('select'+ str(loop))]))

			selectPySparkFactTableQuery = selectPySparkFactTableQuery + 't'+str(loop)+'.id as ' + request.form.get('nameColumn'+ str(loop)) + ', '

			innerJoinsPysparkFactTableQuery = innerJoinsPysparkFactTableQuery + 'INNER JOIN t'+str(loop)+' as t'+str(loop)+' ON factTable._c'+str(loop-1)+' = t'+str(loop)+'.'+request.form.get('nameColumn'+ str(loop)) + ' '

			table.write.format("jdbc")\
			    .option("url", ("jdbc:postgresql://localhost:5432/" + database)) \
			    .option("dbtable", ("\""+database+"-"+request.form.get('nameColumn'+ str(loop))+"\"")) \
			    .option("user", "sebaber12") \
			    .option("password", "sebas") \
			    .option("driver", "org.postgresql.Driver") \
			    .mode("append")\
			    .save()

			w = Window.orderBy('id2')
			table = table.withColumn("id2", F.monotonically_increasing_id()).withColumn("id", F.row_number().over(w))    

			table.registerTempTable("t"+str(loop))

			loop = loop + 1

		creationColumnsFactTable = creationColumnsFactTable[:-2]	

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


		spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", "postgresql-42.2.20.jar").getOrCreate()
		sqlContext = SQLContext(spark)

		data = sqlContext.read.format("csv").option("encoding", "UTF-8").load(os.path.join(UPLOAD_FOLDER,filename))
		


		return '5'

	else:

		return '3'
