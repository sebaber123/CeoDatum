import geopandas as gpd
from requests import Request
from owslib.wfs import WebFeatureService

def extract_data():
	# URL for WFS backend
	url = "http://mapa.educacion.gob.ar/geoserver/ows?service=wfs&version=1.1.0&request=GetCapabilities"

	# See details about this particular WFS
	# -------------------------------------

	# Initialize
	wfs = WebFeatureService(url=url)
	   	
	# Get data from WFS
	# -----------------

	# Fetch the last available layer (as an example) --> 'vaestoruutu:vaki2017_5km'
	layer = list(wfs.contents)[-1]

	# Specify the parameters for fetching the data
	params = dict(service='WFS', version="1.0.0", request='GetFeature',
	      typeName=layer, outputFormat='json')

	# Parse the URL with parameters
	q = Request('GET', url, params=params).prepare().url

	# Read data from URL
	data = gpd.read_file(q)