from flask import redirect, render_template, request, url_for, session, abort, flash
from db import get_db
from models.user import User
import datetime as dt
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

def intento():
    #if not authenticated(session):
    #    abort(401)

    #validacion de permiso
    #if not("estudiante_index" in (session.values())):
    #    abort(401)

    dates = ['21/12/2020','22/12/2020']
    counts = [3,4]

    dictionary=dict(  x=dates, y=counts)
    source = ColumnDataSource(data=dictionary)

    bar = figure(x_range= dictionary['x'], title='bar plot', x_axis_label='x', y_axis_label='y', plot_height=400, plot_width=800)
    #bar.vbar(xbar, top=ybar, color='blue', width=0.5)
    bar.vbar(x='x', top='y', source=source, color='blue', width=0.5)
    bar.y_range.start=0
    hover_tool = HoverTool(tooltips=[
                ("Fecha", "@x"),
                ("Total", "@y")
            ])
    bar.tools.append(hover_tool)

    script, div = components(bar)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')    