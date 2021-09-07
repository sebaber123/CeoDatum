import datetime as dt
from bokeh.plotting import figure, output_file, show
from bokeh.models.tools import HoverTool
import pandas as pd
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from models.visualization import Visualization

def bar_plot(x_axis_name, y_axis_name, data_db_name, table, column_x, column_y):

    data = Visualization.get_data(data_db_name, table, column_x, column_y)    
    y_array = [int(row['cantidad']) for row in data]
    x_array = [str(row['fecha']) for row in data]

    dictionary=dict(  x=x_array, y=y_array)
    source = ColumnDataSource(data=dictionary)

    #aaa


    bar = figure(x_range= dictionary['x'], title='bar plot', x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=400, plot_width=800)
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

    p = figure(title="Title", x_axis_type="datetime", x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=400, plot_width=800)

    p.line(x='x', y='y', source=source, line_width=2)
    hover_tool = HoverTool(tooltips=[
                (x_axis_name, "@x{%F}"),
                (y_axis_name, "@y")
            ],
            formatters = {'@x': 'datetime'}
    )
    p.tools.append(hover_tool)    

    return p