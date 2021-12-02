from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from resources.visualization import bar_plot, line_plot
from models.user import User
from datetime import datetime
from bokeh.plotting import figure, output_file, show
from bokeh.models.tools import HoverTool
import pandas as pd
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from flask_session import Session
from models.establishment import Establishment
from werkzeug.security import generate_password_hash, check_password_hash


def index():
    #if not authenticated(session):
    #    abort(401)

    #validacion de permiso
    #if not("estudiante_index" in (session.values())):
    #    abort(401)

    
    User.db = get_db()
    users = User.get_all_users()

    return render_template('home/index.html', users=users)

"""def intentoLine():
    
    #line plot
    dates = [datetime.strptime('21/12/2020', '%d/%m/%Y'),datetime.strptime('22/12/2020', '%d/%m/%Y'),datetime.strptime('23/12/2020', '%d/%m/%Y')]
    counts = [3,4,8]
    line = line_plot(dates, counts,'fecha', 'cantidad')
    script, div = components(line)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')

def intentoBar():
    #bar plot
    bar2 = bar_plot('fecha', 'cantidad', 'PruebaDatos1', 'prueb', 'fecha', 'boolean = True')
    script, div = components(bar2)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


def embebido():
    return render_template('home/embebido.html')    
"""
def login_form():
    return render_template('user/login_form.html')

def show_register():
    provincias = Establishment.select_provinces()
    return render_template('user/register_form.html', provincias=provincias)

def register_form():
    return redirect('/showRegister')

def forgotPassword():
    return render_template('user/forgot_password_form.html')

def login():
    if request.form['submit'] == 'login':
        name = request.form['name']
        password = request.form['password']
        result = User.login(name, name)
        if result and check_password_hash(result['password'], password):
            session['username'] = result['username']
            session['name'] = result['name']
            session['email'] = result['email']
            session['id'] = result['id']
            session['user_id'] = result[1]
            session['role'] = result['rolename']
            return index()
        else:
            return render_template('user/login_form.html', error="Usuario y/o contraseña incorrectos")
    elif request.form['submit'] == 'register':
        return register_form()

def logout():
    session.clear()
    return redirect(url_for("loginForm"))

def register():
    email = request.form['email']
    if User.emailExist(email):
        return render_template('user/register_form.html', emailExist="El email ya está en uso")
    else:
        username = request.form['username']
        password = request.form['password']
        province = request.form['provinceFormControlSelect']
        city = request.form['cityFormControlSelect']
        institute = request.form['instituteFormControlSelect']
        name = request.form['name']
        surname = request.form['surname']
        birthday = request.form['birthday']
        if username=="" or password=="" or name=="" or surname=="":
            return render_template('user/register_form.html', emptyField="Debe completar todos los campos")
        password = generate_password_hash(password)
        User.register(username, password, province, city, institute, email, name, surname, birthday)
    return render_template('user/login_form.html', registerSuccess="Registro exitoso!")



