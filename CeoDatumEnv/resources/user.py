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



def index():
    #if not authenticated(session):
    #    abort(401)

    #validacion de permiso
    #if not("estudiante_index" in (session.values())):
    #    abort(401)

    
    User.db = get_db()
    users = User.get_all_users()

    return render_template('home/index.html', users=users)

def intentoLine():
    
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

def login_form():
    return render_template('user/login_form.html')

def register_form():
    return render_template('user/register_form.html')

def forgotPassword():
    return render_template('user/forgot_password_form.html')

def login():
    if request.form['submit'] == 'login':
        name = request.form['name']
        password = request.form['password']
        result = User.login(name, password)
        if result:
            return index()
        else:
            return render_template('user/login_form.html', error="Usuario y/o contraseña incorrectos")
    elif request.form['submit'] == 'register':
        return register_form()

def register():
    name = request.form['name']
    password = request.form['password'] 
    email = request.form['email']
    if User.emailExist(email):
        return render_template('user/register_form.html', emailExist="El email ya está en uso")
    User.register(name, password, email)
    return render_template('user/login_form.html', registerSuccess="Registro exitoso!")



