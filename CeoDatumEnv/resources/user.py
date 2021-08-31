from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.user import User



def index():
    #if not authenticated(session):
    #    abort(401)

    #validacion de permiso
    #if not("estudiante_index" in (session.values())):
    #    abort(401)


    User.db = get_db()
    users = User.get_all_users()

    return render_template('home/index.html', users=users)