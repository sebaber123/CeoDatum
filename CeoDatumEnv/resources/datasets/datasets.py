from flask import redirect, render_template, request, url_for, session, abort, flash
from models.dataset import Dataset
from models.visualization import Visualization

pagination = 15

def datasets():
	return render_template('datasets/datasets.html')

def indexPublics(page):

	datasets = Dataset.get_dataset_public(page, pagination)
	
	return render_template('datasets/indexPublics.html', datasets=datasets)	

def show(Bid):	

	if checkSessionCanAccess(Bid):

		sessionId= session['user_id']

		#get the columns of the database
		columns = Visualization.get_db_data(Bid)

		#get the database
		database = Visualization.get_database(Bid)

		canEdit = sessionId == database['database_owner_id']

		#get the structure of the dataset
		databaseStructure = {}

		for column in columns:
			if column['type'] == 'object': 

				dictionaryObject = {}

				columnsOfObject = Visualization.getColumnsOfObject(database['name'],column['name'])

				for columnOfObject in columnsOfObject:
					if columnOfObject['type'] == 'object':

						dictionaryObject[columnOfObject['name']] = generateStructureRecursion(database['name'], column['name'], columnOfObject['name'])

					else:  

						dictionaryObject[columnOfObject['name']] = columnOfObject['type'] 

				databaseStructure[column['name']] = dictionaryObject        

			else: 
				databaseStructure[column['name']] = column['type'] 

		return render_template('datasets/show.html', columns = columns, database = database, databaseStructure = databaseStructure, canEdit = canEdit)



def generateStructureRecursion(databaseName, columnName, columnNameOfObject): 

    dictionaryObject = {}

    columnsOfObject = Visualization.getColumnsOfObject(databaseName,columnName+'-'+columnNameOfObject)

    for columnOfObject in columnsOfObject:
        if columnOfObject['type'] == 'object':

            dictionaryObject[columnOfObject['name']] = generateStructureRecursion(databaseName, columnNameOfObject, columnOfObject['name'])

        else:    
            dictionaryObject[columnOfObject['name']] = columnOfObject['type'] 

    return dictionaryObject  

def checkSessionCanAccess(Bid):
	
	dataset = Dataset.get_dataset(Bid)

	if dataset['share'] == 'publico':

		return True

	else:

		return False	

def editShare():

	datasetId = request.form['id']
	datasetShare = request.form['share']

	Dataset.dataset_edit_share(datasetId, datasetShare)

	

	return redirect('/datasets/show/'+datasetId)



        