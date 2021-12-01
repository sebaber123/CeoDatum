import tweepy
import json
from collections import Counter
from itertools import chain
from flask import redirect, render_template, request, url_for, session, abort, flash, jsonify
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.models.tools import HoverTool, BoxZoomTool, ResetTool, TapTool
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
import math
from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import GraphRenderer, StaticLayoutProvider, Oval, Circle, MultiLine
from bokeh.palettes import Spectral8


def twitter_search():

	return render_template('home/twitterSearch.html')


preposiciones = ['a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en', 'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'según', 'sin', 'so', 'sobre', 'tras', 'versus', 'vía']
articulos = ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas']

def api_twitter_search(stringToSearch, topQuantity, articles, prep):

	wordsToExclude = []

	if articles == 1:
		wordsToExclude = wordsToExclude + articulos

	if prep == 1:
		wordsToExclude = wordsToExclude + preposiciones

	consumer_key="YXA1EA48NTgTWFKeL4ENYdmVl"
	consumer_secret="OpiF2c0NmhqAT7wX6rJZVGs777hHQv3KI3UkyNwBHElC4H2PDi"
	access_token="592381377-xQM7VleetCSVhDA7dUC7ZY3CIRc25TXdHqUyTsal"
	access_token_secret="SniNAifJIoNg3b0wOCbf5Hi6pAyuihFPnp2fx3N9V85gD"

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)

	auth.set_access_token(access_token, access_token_secret)

	api = tweepy.API(auth, wait_on_rate_limit=True)

	tweet_list = []

	counter = Counter()
	counterByWord = {}

	#string_list = ['la casa es grande', 'boca es muy grande', 'boca es mi pasion', 'boca juega 4-4-2', 'boca juega mal pero es mi pasion']

	for tweet in tweepy.Cursor(api.search_tweets, q= (stringToSearch + ' -filter:retweets'), lang='es', tweet_mode='extended').items(10):
			
		tweetTextAux = tweet.full_text.replace("\n", "").lower().split()

		auxCounter = Counter(tweetTextAux)

		counter.update(auxCounter)

		for word in tweetTextAux:
			if word not in counterByWord:
				counterByWord[word] = Counter()
			counterByWord[word].update(auxCounter)
			

	"""for string in string_list:

		counter.update(Counter(string.split()))
		
		for word in string.split():
			if word not in counterByWord:
				counterByWord[word] = Counter()
			counterByWord[word].update(Counter(string.split()))"""

	wordsToPop = []

	for x in counter.keys():
		if x in wordsToExclude:
			wordsToPop.append(x)

	for x in wordsToPop:
		counter.pop(x, None)



	
	mostCommons = counter.most_common(topQuantity)
	relations = []
	relations2 = []
	relationsStart = []
	relationsEnd = []
	for i in range(topQuantity):
		
		relations.append([])


		for j in range(topQuantity):
			


			if i == j:

				
				relations[i].append(0)
				break
			
			else:

				quantity = counterByWord[mostCommons[i][0]][mostCommons[j][0]]

				if  quantity != 0:
					relationsStart.append(i)
					relationsEnd.append(j)
					relations2.append(str(quantity))

				relations[i].append(quantity)

	mostCommonWords = [x[0] for x in mostCommons]
	mostCommonWordsQuantities = [x[1] for x in mostCommons]			

	maxCount = max(mostCommonWordsQuantities)
	radio = []

	#put the radio of the circle depending of the count
	for quantity in mostCommonWordsQuantities:

		radio.append((0.18/maxCount)*quantity + 0.1)
		


	node_indices = list(range(topQuantity))

	plot = figure(x_range=(-4.5,4.5), y_range=(-4.5,4.5))

	graph = GraphRenderer()

	graph.node_renderer.data_source.add(node_indices, 'index')
	graph.node_renderer.data_source.add(radio, 'radio')
	graph.node_renderer.data_source.add(mostCommonWords, 'word')
	graph.node_renderer.data_source.add(mostCommonWordsQuantities, 'quantity')
	graph.node_renderer.glyph = Circle(radius='radio')


	graph.edge_renderer.data_source.data = dict(
	    start=relationsStart,
	    end=relationsEnd)

	### start of layout code
	circ = [i*2*math.pi/topQuantity for i in node_indices]
	x = [math.cos(i)*4 for i in circ]
	y = [math.sin(i)*4 for i in circ]

	graph_layout = dict(zip(node_indices, zip(x, y)))
	graph.layout_provider = StaticLayoutProvider(graph_layout=graph_layout)

	graph.node_renderer.glyph = Circle(radius='radio', fill_color=Spectral8[0])
	graph.node_renderer.selection_glyph = Circle(radius='radio', fill_color=Spectral8[2])
	graph.node_renderer.hover_glyph = Circle(radius='radio', fill_color=Spectral8[1])

	graph.edge_renderer.glyph = MultiLine(line_color="#CCCCCC", line_alpha=0.8, line_width=4)
	graph.edge_renderer.selection_glyph = MultiLine(line_color=Spectral8[2], line_width=4)
	graph.edge_renderer.hover_glyph = MultiLine(line_color=Spectral8[1], line_width=4)


	graph.selection_policy = NodesAndLinkedEdges()


	graph.inspection_policy = NodesAndLinkedEdges()
	#graph.inspection_policy = EdgesAndLinkedNodes()
	
	node_hover_tool = HoverTool(renderers=[graph.node_renderer],tooltips=[("cantidad", "@quantity"), ("palabra", "@word")], show_arrow = False)
	plot.add_tools(node_hover_tool)

	graph.edge_renderer.data_source.add(relations2, 'cantidad')
	edge_hover_tool = HoverTool(renderers=[graph.edge_renderer],tooltips=[("cantidad de apariciones en el mismo tweet", "@cantidad")], line_policy='interp')
	plot.add_tools(edge_hover_tool)
	plot.add_tools(TapTool())

	"""graph.inspection_policy = EdgesAndLinkedNodes()
				graph.edge_renderer.data_source.add(['word1','word2','word3','word4','word5','word6','word7','word8','word9','word10'], 'word')
				edge_hover_tool = HoverTool(tooltips=[("word", "@word")], show_arrow = False)
				plot.add_tools(edge_hover_tool)"""


	plot.renderers.append(graph)

			

	script, div = components(plot)


	return render_template(
		'home/graph.html',
		plot_script=script,
		plot_div=div,
		js_resources=INLINE.render_js(),
		css_resources=INLINE.render_css(),
	).encode(encoding='UTF-8')

	aa		