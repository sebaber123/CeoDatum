from flask import redirect, render_template, request, url_for, session, abort, flash, current_app as app
from db import get_db
from models.user import User
from models.activity import Activity
from werkzeug.utils import secure_filename
from models.configuration import Configuration
import os, shutil


def configuration():
	if session['username']:
		configuration_data = Configuration.get_file_data()
		users = User.get_all_users()
		aaaaaa
		return render_template('configuration/configuration.html', data=configuration_data, users=users)
	else:
		return redirect(url_for('home'))

UPLOAD_FOLDER = 'static/establecimientos_educativos/'
ALLOWED_EXTENSIONS = set(['csv'])

def upload_establishment_file():
	if request.method == 'POST':
		
		folder = os.path.join(UPLOAD_FOLDER)

		file = request.files['file']

		filename = secure_filename(file.filename)
		
		if file and allowed_file(filename):

			filePath = ""
			for fname in os.listdir(folder):
				filePath = os.path.join(folder, fname)
			if filePath:
				try:
					if os.path.isfile(filePath) or os.path.islink(filePath):
						os.unlink(filePath)
					elif os.path.isdir(filePath):
						shutil.rmtree(filePath)
				except Exception as e:
					print('Failed to delete %s. Reason: %s' % (filePath, e))

			file.save(folder + filename)
			Configuration.add_file_data(filename)

	return redirect(url_for('home'))
	


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def cambiar_rol(user_id, role_id):
	if session['username'] and session['role']=="admin":
		Configuration.change_role(user_id, role_id)
	return False
	