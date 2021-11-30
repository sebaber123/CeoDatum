from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.activity import Activity


def activities():
	if session['name']:
		activities = Activity.getActivities(session['id'])
		return render_template('activities/activities.html', activities=activities)
	else:
		return render_template('/')

def new_activity():
	if session['role']=='professor':
		return render_template('activities/new_activity.html')
	else:
		return redirect(url_for('home'))