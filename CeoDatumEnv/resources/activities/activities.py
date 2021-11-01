from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db

def activities():
	return render_template('activties/activities.html')