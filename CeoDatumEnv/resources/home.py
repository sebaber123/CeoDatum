from flask import redirect, render_template, request, url_for, session, abort, flash, jsonify
import os
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'csv', 'json'])

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
            return '5'
        else:
        	return '4'    