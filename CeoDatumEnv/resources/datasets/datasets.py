from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db

def datasets():
	return render_template('datasets/datasets.html')