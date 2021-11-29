import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService
from models.establishment import Establishment
import os
from pyspark.sql import SQLContext, Row, SparkSession
from pyspark import SparkContext, SparkConf
from pyspark.sql import types 
from pyspark.sql import functions as F
from pyspark.sql.functions import *
from pyspark.sql import  Window
from pyspark.sql.types import DateType
from flask import jsonify


UPLOAD_FOLDER = 'static/establecimientos_educativos/'
filename = 'establecimientos_educativos.csv'


def extract_data():
	table_name = 'establecimientos_educativos'
	spark = SparkSession.builder.appName("CeoDatum").config("spark.jars", (os.path.join("resources","postgresql-42.3.0.jar"))).getOrCreate()
	sqlContext = SQLContext(spark)
	data = spark.read.csv(UPLOAD_FOLDER + filename, header=True, mode="DROPMALFORMED")
	data = data.withColumnRenamed("Jurisdicción", "jurisdiccion")
	provincias = extract_provinces(spark, sqlContext, data)
	ciudades = extract_cities(spark,sqlContext,data,provincias)
	Establishment = extract_establishment(spark,sqlContext,data,ciudades)
	return True

def extract_provinces(spark, sqlContext, data):
	table_name = 'province'
	provincias = data.select("jurisdiccion").distinct()
	headers = provincias.first().__fields__
	provincias_table = Establishment.create_table_with_id(table_name, headers)
	provincias.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/CeoDatum")) \
				    .option("dbtable", "province") \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()
	provincias_result = Establishment.select_all(table_name)
	return provincias_result

def extract_cities(spark, sqlContext, data, provincias):
	table_name = 'city'
	ciudades = data.select("Localidad", "jurisdiccion", "Código localidad", "Código de área").distinct()
	ciudades = ciudades.withColumnRenamed("Código localidad", "codigo_localidad").withColumnRenamed("Código de área", "codigo_de_area")
	df = spark.createDataFrame(provincias, schema= ["id", "nombre"])
	df.registerTempTable("df_temp")
	ciudades.registerTempTable("ciudades_temp")
	result = sqlContext.sql("SELECT * FROM (SELECT id as id_provincia, Localidad as localidad, ROW_NUMBER() OVER (PARTITION by Localidad ORDER BY codigo_localidad DESC) as rn, codigo_localidad, codigo_de_area from ciudades_temp INNER JOIN df_temp ON df_temp.nombre = ciudades_temp.jurisdiccion) a WHERE rn = 1")
	headers = result.first().__fields__
	ciudades_table = Establishment.create_table_with_id(table_name, headers)
	result.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/CeoDatum")) \
				    .option("dbtable", "city") \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()
	ciudades_result = Establishment.select_all(table_name)
	return ciudades_result

def extract_establishment(spark, sqlContext, data, ciudades):
	table_name = 'establishment'
	establecimientos = data.select("CUE Anexo", "Nombre", "Ámbito", "Domicilio", "Localidad", "Teléfono", "Mail").distinct()
	establecimientos = establecimientos.withColumnRenamed("CUE Anexo", "cue").withColumnRenamed("Ámbito", "ambito").withColumnRenamed("Teléfono", "telefono")
	df = spark.createDataFrame(ciudades, schema= ["id", "id_provincia", "nombre_ciudad", "codigo","codigo_area"])
	df.registerTempTable("df_temp")
	establecimientos.registerTempTable("establecimientos_temp")
	result = sqlContext.sql("SELECT DISTINCT id as id_ciudad, cue, Nombre as nombre, ambito, Domicilio as domicilio, telefono, Mail as mail from establecimientos_temp INNER JOIN df_temp ON df_temp.nombre_ciudad = establecimientos_temp.Localidad")
	headers = result.first().__fields__
	establecimientos_table = Establishment.create_table_with_id(table_name, headers)
	result.write.format("jdbc")\
				    .option("url", ("jdbc:postgresql://localhost:5432/CeoDatum")) \
				    .option("dbtable", "establishment") \
				    .option("user", "sebaber12") \
				    .option("password", "sebas") \
				    .option("driver", "org.postgresql.Driver") \
				    .mode("append")\
				    .save()
	establecimientos_result = Establishment.select_all(table_name)
	return establecimientos_result

def get_cities_by_province(province):
	ajaxData = Establishment.get_cities_by_province(province)
	return jsonify(result = ajaxData)

def get_establishments_by_city(city):
	ajaxData = Establishment.get_establishments_by_city(city)
	return jsonify(result = ajaxData)
