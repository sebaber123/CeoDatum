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
from math import pi
from bokeh.transform import cumsum
from bokeh.palettes import Category20, cividis, Set3, Set1, Category10


#return the plotter page
def plotter(Bid):

    #get the columns of the database
    columns = Visualization.get_db_data(Bid)
    
    #get the database
    database = Visualization.get_database(Bid)

    return render_template('home/plotter.html', columns = columns, database= database)  

#transform the string of conditions to the format that the query needs
def conditionsToString(database, axis, condition):    

    #array of the columns that will need the query to have the columns of the conditions
    columnsToInner = []
    # string of the inner joins
    innerColumnsCondition = ''
    
    #string of the conditions that will use the query
    queryCondition = ''

    #dictionary of conditions positive
    queryConditionPositive = {}

    #string of negative conditions
    queryConditionNegative = '' 

    #axi_x name
    axie_x = ''

    #axi_y name
    axie_y = ''

    #position to add to the tX (rename of the inner joins in the query). only 1 if only the axi_x is defined
    positionToAdd = 1


    if len(axis)>1:
        
        #get the values of the parameters
        axie_x = axis[0]
        axie_y = axis[1]

        #position to add to the tX (rename of the inner joins in the query). add 2 if only the axi_x and axi_y is defined
        positionToAdd = 2

    else:
        
        #get the value of the parameter
        axie_x = axis    


    #check if there is a condition to transform
    if condition != None:
        
        #loop through the conditions. The conditions in the string are divided by '***'
        for cond in condition.split(sep='***'):
            
            #string condition 
            columnCondition = ''
            
            #position to add to the tX (rename of the inner joins in the query). only 1 if only the axi_x is defined
            pos = -1

            #check if the condition is not negative
            if cond.find('!=') == -1:                                    
                
                #get the name of the column (first part of the condition)
                columnCondition = cond.split(sep='=')[0].strip()
                
                #check if the condition is 'mayor que' or 'menor que'
                if columnCondition[-1] == '>' or columnCondition[-1] == '<':
                    
                    #if the condition is 'mayor que' or 'menor que' delete the white space and the '<' or '>'
                    columnCondition = columnCondition[:-2]
 

                #check if the column is in the array
                if columnCondition in columnsToInner:

                    #if the column is in the array add the index to the position to get the tX (rename of the inner joins in the query)
                    pos = columnsToInner.index(columnCondition) + positionToAdd
                else:

                    #check if the column is equal to the axi_x
                    if columnCondition == axie_x:

                        #if the column is equal to the axi_x the tX is 0
                        pos = 0
                    else:

                        #check if the column is equal to the axi_y
                        if columnCondition == axie_y:
                            
                            #if the column is equal to the axi_y the tX is 0
                            pos = 1    
                        
                        else:                                

                            #else get the length and add it to the position to get the tX (rename of the inner joins in the query)
                            pos = len(columnsToInner) + positionToAdd


                #if the condition is between add the tX to the seccond condition
                if (cond.find('>=') != -1 and cond.find('<=') != -1) :

                    #get the column
                    secondCond = cond.find(columnCondition + ' <=')        
                    
                    #put the tX in the second condition
                    cond = cond[:secondCond] + 't' + str(pos) + '.' + cond[secondCond:] 

                #If the 'columnCondition' not in 'QueryConditionPositive' it means that, have to create the array of that column
                if columnCondition not in queryConditionPositive:
                    
                    #create the array
                    queryConditionPositive[columnCondition] = []    

                #add the condition to the corresponding array
                queryConditionPositive[columnCondition].append('t'+ str(pos) +'.'+ cond)                    


            #it means that the condition is negative
            else:

                #get the name of the column (first part of the condition)
                columnCondition = cond.split(sep='!=')[0].strip()

                #check if the column is in the array
                if columnCondition in columnsToInner:

                    #if the column is in the array add the index to the position to get the tX (rename of the inner joins in the query)
                    pos = columnsToInner.index(columnCondition) + positionToAdd
                else:

                    #check if the column is equal to the axi_x
                    if columnCondition == axie_x:

                        #if the column is equal to the axi_x the tX is 0
                        pos = 0
                    else:

                        #check if the column is equal to the axi_y
                        if columnCondition == axie_y:
                            
                            #if the column is equal to the axi_y the tX is 0
                            pos = 1    
                        
                        else:                                

                            #else get the length and add it to the position to get the tX (rename of the inner joins in the query)
                            pos = len(columnsToInner) + positionToAdd
            
                
                #if the string of negative condition is not empty add " AND " to separate the conditions
                if queryConditionNegative != '':
                    queryConditionNegative = queryConditionNegative + " AND "

                #Add the condition
                queryConditionNegative = queryConditionNegative + 't'+ str(pos) +'.'+ columnCondition +" != " + cond.split(sep='=')[1].strip()+ ""


            if columnCondition != axie_x and columnCondition != axie_y :
                if columnCondition not in columnsToInner:
                    columnsToInner.append(columnCondition)    
           

        #loop through the columnsToInner
        for column in columnsToInner:

            #add the inner join to the column to the string of inner joins
            innerColumnsCondition = innerColumnsCondition + " inner join \""+database+"-" +column + "\" as t"+str(columnsToInner.index(column)+positionToAdd)+" on t." +column + "  = t"+str(columnsToInner.index(column)+positionToAdd)+".id "

        #add the negative part of conditions
        #if there is no negative conditions just add a '(False)'
        if not queryConditionNegative:
            queryCondition = "where (False) OR"

        #else, add the QueryConditionNegative
        else:
            queryCondition = "where (" +queryConditionNegative+ ") OR "                

        #add the positive part of conditions
        #if there is no positive conditions just add a '(False)'    
        if not queryConditionPositive:            
            queryCondition = queryCondition + " (False) "

        #else, add the positive condition
        else:

            #the positive condition is divided by 'OR' in the same column and by 'AND' in the diferent columns 
            for key in queryConditionPositive:
                queryCondition = queryCondition + '('

                for conditionpositive in queryConditionPositive[key]:
                    queryCondition = queryCondition + conditionpositive + ' OR '

                queryCondition = queryCondition[:-3] + ') AND '

            #delete the last 'AND ' of the string
            queryCondition = queryCondition[:-4]        

    #return the query condition and the inner joins
    return [queryCondition, innerColumnsCondition]       


#make the bar graph
def graphBar(database, x_axie, condition):
    
    #call the method to transform the conditions
    ConditionAndColumns = conditionsToString(database, x_axie, condition)        


    #make the bar plot
    bar2 = bar_plot(x_axie, 'cantidad', database, database, x_axie, ConditionAndColumns[0], ConditionAndColumns[1])
    
    #method that return the script and div that is needed to create the graph in the page  
    script, div = components(bar2)


    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')

#generate the bar plot
def bar_plot(x_axis_name, y_axis_name, data_db_name, table, column_x, condition, innerColumnsCondition):

    #get the data of the database
    data = Visualization.get_data(data_db_name, table, column_x, condition, innerColumnsCondition)    
    
    #get the counts of the data
    y_array = [int(row['count']) for row in data]
    
    #get the x axi value
    x_array = [str(row[column_x]) for row in data]

    
    #create a dictionary that  with the 'x_array' and 'y_array' arrays
    dictionary=dict(  x=x_array, y=y_array)
    
    #transform the dictionary to a 'ColumnDataSource' (needed by the graph)
    source = ColumnDataSource(data=dictionary)

    #generate the graph
    bar = figure(x_range= dictionary['x'], title='bar plot', x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=500, plot_width=800)
    bar.vbar(x='x', top='y', source=source, color='blue', width=0.5)
    bar.y_range.start=0
    
    #on hover tool
    hover_tool = HoverTool(tooltips=[
                (x_axis_name, "@x"),
                (y_axis_name, "@y")
            ])
    
    #add on hover tool to the graph
    bar.tools.append(hover_tool)

    #return the graph
    return bar

#return the graph line
def graphLine(database, x_axie, condition):

    #call the method to transform the conditions    
    ConditionAndColumns = conditionsToString(database, x_axie, condition)    

    #make the line plot
    line = line_plot(x_axie, 'cantidad', database, database, x_axie, ConditionAndColumns[0], ConditionAndColumns[1])
    
    #method that return the script and div that is needed to create the graph in the page 
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
    
    #get the data of the database
    data = Visualization.get_data(data_db_name, table, column_x, condition, innerColumnsCondition)

    #get the counts of the data
    y_array = [int(row['count']) for row in data]
    
    #get the x axi value
    x_array = [datetime.strptime(str(row[column_x]), '%Y-%m-%d') for row in data]

    #var used to calculate the acumulative count
    countsTotal = []
    count = 0

    #calculate the acumulative count
    for i in range(len(y_array)):
        count = count + y_array[i]
        countsTotal.append(count)

    
    #create a dictionary that  with the 'x_array' and 'y_array' arrays
    dictionary=dict(  x=x_array, y=countsTotal)
    
    #transform the dictionary to a 'ColumnDataSource' (needed by the graph)
    source = ColumnDataSource(data=dictionary)

    #generate the graph
    p = figure(title="Title", x_axis_type="datetime", x_axis_label=x_axis_name, y_axis_label=y_axis_name, plot_height=500, plot_width=800)
    p.line(x='x', y='y', source=source, line_width=2)
    p.circle(x='x', y='y', source=source, fill_color="white", size=8)

    #on hover tool
    hover_tool = HoverTool(tooltips=[
            ("Fecha", "@x{%F}"),
            ("Total", "@y")
        ],
        formatters = {'@x': 'datetime'}
            
    )

    #add on hover tool to the graph
    p.tools.append(hover_tool)    

    #return the graph
    return p


#generate the string of the counts for the data table
def counts_query_for_data_table(database, column, condition):
    
    #get the values of column in the database
    columnData = Visualization.getColumnData(database, column, condition)

    stringCounts = ''
    
    #generate the counts
    for x in columnData:
        stringCounts = stringCounts + 'count(case t1.'+column+' when \''+str(x[1])+'\' then 1 else null end) as \"'+ str(x[1]) + '\", '

    #delete the last ', ' of the string
    stringCounts = stringCounts[:-2] 
    
    #add the name of column of the count (used in the headers of the data table)
    columnNames = [str(row[1]) for row in columnData]

    return [stringCounts, columnNames]
        
    
#generate the data table
def data_table(database, rowName, column, condition):

    #check if the column is defined to know the counts of rows that must be calculated (if its not defined just count all the rows)
    if column != 'undefined':

        #call the method to transform the conditions
        conditionAndColumns = conditionsToString(database, [rowName, column], condition) 

        #store the conditions that alterate the columns of the table
        conditionsOfColumn = ''

        #check if there is any condition
        if condition != None:

            #loop through the conditions. The conditions in the string are divided by '***'
            for cond in condition.split(sep='***'):

                #check if the columns of the condition is the same of the column of the datatable 
                if (cond[:+len(column)] == column):

                    #add the condition to the string
                    conditionsOfColumn = conditionsOfColumn + cond + '***'

            #delete the last '***'
            conditionsOfColumn = conditionsOfColumn[:-3]        

        #counts of the rows in the query
        counts = ''

        #check if there are conditions of the column selected for the table
        if conditionsOfColumn:

            #call the method to transform the conditions
            queryConditionsOfColumns = conditionsToString(database,  [rowName, column], conditionsOfColumn) 
            
            #generate the counts for the columns needed
            counts = counts_query_for_data_table(database, column, queryConditionsOfColumns[0])
        
        else:

            #generate the counts for all the columns
            counts = counts_query_for_data_table(database, column, '') 

        #check if there is a condition in the parameters
        if condition != None:    

            #get the data of the database
            data = Visualization.get_data_for_data_table(database, rowName, column, conditionAndColumns[0], conditionAndColumns[1], counts[0])
        else:

            #get the data of the database
            data = Visualization.get_data_for_data_table(database, rowName, column, '', '', counts[0])        

        
    
    else:
        
        #call the method to transform the conditions
        conditionAndColumns = conditionsToString(database, rowName, condition)

        #Add the count if there is no column defined
        counts = ['COUNT(t.id) as count', ['cantidad']]

        #get the data of the database
        data = Visualization.get_data_for_data_table_without_column(database, rowName, conditionAndColumns[0], conditionAndColumns[1], counts[0])

    #Array of 'rowNames' returned by the query
    columnRow = [str(row[rowName]) for row in data]

    #create a dictionary that  will be used by the data table
    dictionary = dict()

    #add the array to the dictionary
    dictionary[rowName] = columnRow

    #add the counts to the table and the headers of the columns of counts in the table
    for x in range(len(counts[1])):
        dictionary[counts[1][x]] = [int(row[x+1]) for row in data]    

    #transform the dictionary to a 'ColumnDataSource' (needed by the table)
    source = ColumnDataSource(dictionary)

    #add the first column
    dataTableColumns = [TableColumn(field=rowName, title=rowName)]

    #add the others columns
    for x in counts[1]:
        dataTableColumns.append(TableColumn(field=x, title=x))

    #create the data table
    dataTable = DataTable(source=source, columns=dataTableColumns, index_position=None, width=800, height=500)

    #method that return the script and div that is needed to create the graph in the page 
    script, div = components(dataTable)

    #return the template
    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


#generate the pie chart
def pie_plot(rowName, data_db_name, table, column_x, condition, innerColumnsCondition):

    #get the data of the database
    data = Visualization.get_data(data_db_name, table, column_x, condition, innerColumnsCondition)

    #get the names of each portion of the graph
    rowData = [str(row[rowName]) for row in data]

    #get the counts of the data
    counts = [int(row['count']) for row in data]

    #create the dictionary
    dictionary = {}

    #put the data in a dictionary
    for i in range(len(rowData)):
        dictionary[rowData[i]] = counts[i]

    #generate the data structure needed by the graph
    data = pd.Series(dictionary).reset_index(name='value').rename(columns={'index':rowName})
    
    #calculate the total of the counts
    totalSum = data['value'].sum()

    #calculate the angle of each portion of the pie chart
    data['angle'] = data['value']/totalSum * 2*pi
    data['percentage'] = data['value']/totalSum * 100
    
    #calculate the color for each portion
    if len(data['angle'])<=2:
        colors = Category10[3]
        data['color'] = colors[:-(3-len(data['angle']))]
    else:    
        data['color'] = Category10[(len(data['angle']))]

        
    #generate the graph
    p = figure(plot_height=350, title="Pie Chart", x_range=(-0.5, 1.0))
    p.wedge(x=0, y=1, radius=0.4,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field=rowName, source=data)

    #on hover tool 
    hover_tool = HoverTool(tooltips=[
                (rowName, "@"+rowName),
                ("porcentaje", "@percentage"+" %"),
                ("cantidad", "@value")
            ])

    #add on hover tool to the graph
    p.tools.append(hover_tool)  

    #return the graph
    return p

#generate the pie chart
def pie_chart(database, rowName, condition):

    #call the method to transform the conditions
    ConditionAndColumns = conditionsToString(database, rowName, condition)  

    #call the method that generate the graph
    graph = pie_plot(rowName, database, database, rowName, ConditionAndColumns[0], ConditionAndColumns[1])
    
    #method that return the script and div that is needed to create the graph in the page 
    script, div = components(graph)
 
    return render_template(
        'home/intento.html',
        plot_script=script,
        plot_div=div,
        js_resources=INLINE.render_js(),
        css_resources=INLINE.render_css(),
    ).encode(encoding='UTF-8')


#return the values of a table
def ajaxGetColumnData(database, column):
    
    ajaxData = Visualization.getColumnData(database, column, '')

    y = 0
    if(str(type(ajaxData[0][1])) == "<class 'datetime.date'>"):
        for x in ajaxData:
            x[1] = str(x[1])


    return jsonify(result = ajaxData)
