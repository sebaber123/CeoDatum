from flask import redirect, render_template, request, url_for, session, abort, flash
import datetime as dt
from bokeh.plotting import figure, output_file, show
from bokeh.models.tools import HoverTool
import pandas as pd
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from models.visualization import Visualization


def embebido(Bid):

    columns = Visualization.get_db_data(1)

    return render_template('home/embebido.html', columns = columns)  


def intentoBar(x_axie):
    


    #bar plot
    bar2 = bar_plot('fecha', 'cantidad', 'PruebaDatos1', 'prueb', x_axie, '')
    script, div = components(bar2)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


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


def bar_plot(x_axis_name, y_axis_name, data_db_name, table, column_x, condition):

    data = Visualization.get_data(data_db_name, table, column_x, condition)    
    y_array = [int(row['count']) for row in data]
    x_array = [str(row[column_x]) for row in data]

    dictionary=dict(  x=x_array, y=y_array)
    source = ColumnDataSource(data=dictionary)


    bar = figure(x_range= dictionary['x'], title='bar plot', x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=500, plot_width=800)
    bar.vbar(x='x', top='y', source=source, color='blue', width=0.5)
    bar.y_range.start=0
    hover_tool = HoverTool(tooltips=[
                (x_axis_name, "@x"),
                (y_axis_name, "@y")
            ])
    bar.tools.append(hover_tool)

    return bar

#line plot with datetimes
def line_plot(x_axis_array, y_axis_array, x_axis_name, y_axis_name):
    
    
    dictionary=dict(  x=x_axis_array, y=y_axis_array)
    source = ColumnDataSource(data=dictionary)

    p = figure(title="Title", x_axis_type="datetime", x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=500, plot_width=800)

    p.line(x='x', y='y', source=source, line_width=2)
    hover_tool = HoverTool(tooltips=[
                (x_axis_name, "@x{%F}"),
                (y_axis_name, "@y")
            ],
            formatters = {'@x': 'datetime'}
    )
    p.tools.append(hover_tool)    

    return p