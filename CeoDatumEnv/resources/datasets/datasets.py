from flask import redirect, render_template, request, url_for, session, abort, flash
from models.dataset import Dataset
from models.visualization import Visualization
from models.user import User


pagination = 5

def datasets():
	return render_template('datasets/datasets.html')	

def getAvailablePages(actualPage, maxPage):

	pagesArray = []

	if maxPage > 4:

		if actualPage < 4:
			
			pagesArray = [1,2,3,4,5]

		else:

			if maxPage >= actualPage+2:

				pagesArray = [actualPage-2, actualPage-1, actualPage, actualPage + 1, actualPage + 2]

			else:
				
				pagesArray = [maxPage - 4, maxPage - 3, maxPage - 2, maxPage - 1, maxPage]	
	else:

		for x in range(maxPage):

			pagesArray.append(x+1)		

	return pagesArray		


def indexPublics(page):

	datasets = Dataset.get_dataset_public(page, pagination)

	maxPage = Dataset.max_page_publics(pagination)

	availablePages = getAvailablePages(page, maxPage)
	
	return render_template('datasets/index.html', datasets=datasets, nombre='Públicos', name='publics', availablePages=availablePages, maxPage=maxPage, actualPage=page)	

def indexProtecteds(page):

	establishmentId = (User.get_user_by_id(session['id']))['establishment_id']

	datasets = Dataset.get_dataset_protected(session['id'], establishmentId, page, pagination)

	maxPage = Dataset.max_page_protecteds(pagination, establishmentId, session['id'])

	availablePages = getAvailablePages(page, maxPage)
	
	return render_template('datasets/index.html', datasets=datasets, nombre='protegidos', name='protecteds', availablePages=availablePages, maxPage=maxPage, actualPage=page)	

def indexPrivates(page):

	datasets = Dataset.get_dataset_privates(session['id'], page, pagination)

	maxPage = Dataset.max_page_privates(pagination, session['id'])

	availablePages = getAvailablePages(page, maxPage)
	
	return render_template('datasets/index.html', datasets=datasets, nombre='privados', name='privates', availablePages=availablePages, maxPage=maxPage, actualPage=page)			

def show(Bid):	

	if checkSessionCanAccess(Bid):

		sessionId= session['id']

		#get the columns of the database
		columns = Visualization.get_db_data(Bid)

		#get the database
		database = Dataset.get_dataset_with_owner(Bid)

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

	establishmentId = (User.get_user_by_id(session['id']))['establishment_id']
	
	return Dataset.check_can_access_to_dataset(Bid, session['id'], establishmentId)

def editShare():

	datasetId = request.form['id']
	datasetShare = request.form['share']

	Dataset.dataset_edit_share(datasetId, datasetShare)

	establishmentId = (User.get_user_by_id(session['id']))['establishment_id']

	if datasetShare == 'protegido':
		
		Dataset.add_dataset_to_stablisment(datasetId, establishmentId)
	else:	

		Dataset.delete_dataset_from_stablisment(datasetId, establishmentId)


	return redirect('/datasets/show/'+datasetId)



        