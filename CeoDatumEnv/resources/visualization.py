from flask import redirect, render_template, request, url_for, session, abort, flash, jsonify
from datetime import datetime 
from bokeh.plotting import figure, output_file, show
from bokeh.models.tools import HoverTool
import pandas as pd
from bokeh.models import ColumnDataSource, Div, Select, Slider, TextInput
from bokeh.models.widgets import DataTable, DateFormatter, TableColumn
from bokeh.io import curdoc
from bokeh.resources import INLINE
from bokeh.embed import components
from models.visualization import Visualization


def embebido(Bid):

    columns = Visualization.get_db_data(1)
    database = Visualization.get_database(1)

    return render_template('home/embebido.html', columns = columns, database= database)  

def conditionsToString(database, axis, condition):    

    columnsToInner = []
    innerColumnsCondition = ''
    queryCondition = ''
    queryConditionPositive = {}
    queryConditionNegative = '' 
    cantNegative = 0
    axie_x = ''
    axie_y = ''
    positionToAdd = 1

    if len(axis)>1:
        
        axie_x = axis[0]
        axie_y = axis[1]
        positionToAdd = 2

    else:
        
        axie_x = axis    


    if condition != None:
        
        for cond in condition.split(sep='***'):
            
            
            columnCondition = ''
            pos = -1

            if cond.find('!=') == -1:                                    
                


                columnCondition = cond.split(sep='=')[0].strip()
                
                if columnCondition[-1] == '>' or columnCondition[-1] == '<':
                    columnCondition = columnCondition[:-2]
 

                if columnCondition in columnsToInner:
                    pos = columnsToInner.index(columnCondition) + positionToAdd
                else:
                    if columnCondition == axie_x:
                        pos = 0
                    else:
                        if columnCondition == axie_y:
                            pos = 1    
                        
                        else:                                
                            pos = len(columnsToInner) + positionToAdd


                #cuando es between agregar el tx. a la segunda condicion
                if (cond.find('>=') != -1 and cond.find('<=') != -1) :
                    secondCond = cond.find(columnCondition + ' <=')        
                    cond = cond[:secondCond] + 't' + str(pos) + '.' + cond[secondCond:] 


                if columnCondition not in queryConditionPositive:
                    
                    queryConditionPositive[columnCondition] = []    

                #queryConditionPositive[columnCondition].append('t'+ str(pos) +'.'+ columnCondition +" = \'" + cond.split(sep='=')[1].strip()+ "\'")
                queryConditionPositive[columnCondition].append('t'+ str(pos) +'.'+ cond)                    



            else:

                columnCondition = cond.split(sep='!=')[0].strip()

                if columnCondition in columnsToInner:
                    pos = columnsToInner.index(columnCondition) + positionToAdd
                else:
                    if columnCondition == axie_x:
                        pos = 0
                    else:    
                        if columnCondition == axie_y:
                            pos = 1    
                        
                        else:                                
                            pos = len(columnsToInner) + positionToAdd 
                

                if cantNegative > 0:
                    queryConditionNegative = queryConditionNegative + " AND "

                queryConditionNegative = queryConditionNegative + 't'+ str(pos) +'.'+ columnCondition +" != \'" + cond.split(sep='=')[1].strip()+ "\'"
                cantNegative = cantNegative + 1


            if columnCondition != axie_x and columnCondition != axie_y :
                if columnCondition not in columnsToInner:
                    columnsToInner.append(columnCondition)    
           

        for column in columnsToInner:
            innerColumnsCondition = innerColumnsCondition + " inner join \""+database+"-" +column + "\" as t"+str(columnsToInner.index(column)+positionToAdd)+" on t." +column + "  = t"+str(columnsToInner.index(column)+positionToAdd)+".id "

        if not queryConditionNegative:
            queryCondition = "where (False) OR"

        else:
            queryCondition = "where (" +queryConditionNegative+ ") OR "                

        if not queryConditionPositive:            
            queryCondition = queryCondition + " (False) "

        else:

            for key in queryConditionPositive:
                queryCondition = queryCondition + '('

                for conditionpositive in queryConditionPositive[key]:
                    queryCondition = queryCondition + conditionpositive + ' OR '

                queryCondition = queryCondition[:-3] + ') AND '

            queryCondition = queryCondition[:-4]        


    return [queryCondition, innerColumnsCondition]       


def graphBar(database, x_axie, condition):
    
    ConditionAndColumns = conditionsToString(database, x_axie, condition)        


    #bar plot
    bar2 = bar_plot(x_axie, 'cantidad', database, database, x_axie, ConditionAndColumns[0], ConditionAndColumns[1])
    script, div = components(bar2)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


def bar_plot(x_axis_name, y_axis_name, data_db_name, table, column_x, condition, innerColumnsCondition):

    data = Visualization.get_data(data_db_name, table, column_x, condition, innerColumnsCondition)    
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

def graphLine(database, x_axie, condition):

    ConditionAndColumns = conditionsToString(database, x_axie, condition)    

    line = line_plot(x_axie, 'cantidad', database, database, x_axie, ConditionAndColumns[0], ConditionAndColumns[1])
    script, div = components(line)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')

#line plot with datetimes
def line_plot(x_axis_name, y_axis_name, data_db_name, table, column_x, condition, innerColumnsCondition):
    
    
    data = Visualization.get_data(data_db_name, table, column_x, condition, innerColumnsCondition)
    y_array = [int(row['count']) for row in data]
    x_array = [datetime.strptime(str(row[column_x]), '%Y-%m-%d') for row in data]

    

    countsTotal = []
    count = 0

    for i in range(len(y_array)):
        count = count + y_array[i]
        countsTotal.append(count)

    

    dictionary=dict(  x=x_array, y=countsTotal)
    source = ColumnDataSource(data=dictionary)

    p = figure(title="Title", x_axis_type="datetime", x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=500, plot_width=800)

    #p.line(x=x_array, y=y_array, line_width=2)
    p.line(x='x', y='y', source=source, line_width=2)
    p.circle(x='x', y='y', source=source, fill_color="white", size=8)


    hover_tool = HoverTool(tooltips=[
            ("Fecha", "@x{%F}"),
            ("Total", "@y")
        ],
        formatters = {'@x': 'datetime'}
            
    )
    p.tools.append(hover_tool)    

    return p


def counts_query_for_data_table(database, column):
    
    columnData = Visualization.getColumnData(database, column)

    stringCounts = ''
    
    for x in columnData:
        stringCounts = stringCounts + 'count(case t1.'+column+' when \''+str(x[1])+'\' then 1 else null end) as '+ str(x[1]) + ', '

    stringCounts = stringCounts[:-2] 
    
    columnNames = [str(row[1]) for row in columnData]

    return [stringCounts, columnNames]

        
    

def data_table(database, rowName, column, condition):

    conditionAndColumns = conditionsToString(database, [rowName, column], condition)  

    counts = counts_query_for_data_table(database, column)

    data = Visualization.get_data_for_data_table(database, rowName, column, conditionAndColumns[0], conditionAndColumns[1], counts[0])

    columnRow = [str(row[rowName]) for row in data]

    dictionary = dict()

    dictionary[rowName] = columnRow

    for x in range(len(counts[1])):
        dictionary[counts[1][x]] = [int(row[x+1]) for row in data]    

    source = ColumnDataSource(dictionary)

    dataTableColumns = [TableColumn(field=rowName, title=rowName)]

    for x in counts[1]:
        dataTableColumns.append(TableColumn(field=x, title=x))

    dataTable = DataTable(source=source, columns=dataTableColumns, index_position=None, width=800, height=500)

    script, div = components(dataTable)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


def ajaxGetColumnData(database, column):
    
    ajaxData = Visualization.getColumnData(database, column)

    y = 0
    if(str(type(ajaxData[0][1])) == "<class 'datetime.date'>"):
        for x in ajaxData:
            x[1] = str(x[1])


    return jsonify(result = ajaxData)
