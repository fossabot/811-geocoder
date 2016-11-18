######################################################################################
# Locate Geocoder with KML writing													 #
# Feed in a CSV, receive stdout Lat/Long and KML Long/Lat 							 #
# Author: Stephan Garland, Carroll White REMC										 #
# Shoutout to Wiktor Stribiżew on StackOverflow for the regex						 #
# Directions: Create a CSV that has a header named Address, containing the address	 #
#             The regex is setup for USIC's naming scheme for addresses:			 #
#			  $HOUSE_NUM $STREET_NAME $TOWN $NEAREST_INTERSECTION					 #
#			  $INTERSECTING_STREET_1_NAME $TOWN $INTERSECTING_STREET_2_NAME			 #
#			  Run the script, import the KML into ArcEarth with your territory KML   #
# TODO: Create error checking for out-of-bounds addresses that don't code			 #
######################################################################################

import geocoder, csv, simplekml, re

file = "P:/Geocoding Test.csv" # Edit to change location of incoming CSV file
kml = simplekml.Kml()
kmlSaveLoc = "P:/Geo Results.kml" # Edit to change location and name of generated KML file

# Python 2.7 throws an insecure platform warning, and urllib3 won't install on the customized Python build I have to use
# If it did, the try would succeed. As it is, the warnings just clutter up stdout, so they're suppressed
try:
	import urllib3.contrib.pyopenssl
	urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
	import requests
	from requests.packages.urllib3.exceptions import InsecurePlatformWarning
	requests.packages.urllib3.disable_warnings()
		
with open(file,'r') as listFile:
	reader = csv.DictReader(listFile, delimiter = ',', quotechar = '"')
	
	for row in reader:
		testAddr = row['Address']
		if not testAddr[:1].isdigit(): # If the address doesn't start with a number, it's an intersection
			# Regex: \s+ - whitespace character[1-inf, greedy]; \S+ - non-whitespace character[1-inf, greedy]; \s* - whitespace character[0-inf, greedy]; (.*) - any character
			readAddr = re.compile(r"(Avenue|Lane|Road|Court|Boulevard|Drive|Street|Ave|Dr|Rd|Ct|Blvd|Ln|St)\s+(\S+)\s*(.*)", re.I)
			subAddr = row['Address'] # Pull the non-parsed address out, which will include the city
			fixedAddr = re.sub(readAddr, r'\1 & \3 \2', subAddr) # Run it through the regex, group it as 1 & 3 then 2, which generates an intersection and city
			kmlAddr = re.sub(readAddr, r'\1 & \3', subAddr) # For tagging the map point, ignore the city to save space on map
			catAddr = fixedAddr + " " + "IN" # Cat address and defined state for geocoding - replace "IN" with your state
			geoResult = geocoder.arcgis(catAddr).latlng # Run above list through ArcGIS via geocoder, then save Lat/Long
			reverseGeo = geoResult[::-1] # simplekml needs Long/Lat, and reversed() wasn't working, so slice the list
			kml.newpoint(name = kmlAddr, coords = [reverseGeo])
		else:
			readAddr = re.compile(r"(Avenue|Lane|Road|Court|Boulevard|Drive|Street|Ave|Dr|Rd|Ct|Blvd|Ln|St)\s+(\S+)\s*(.*)", re.I) # Otherwise, assume it has a street number
			subAddr = row['Address']
			fixedAddr = re.sub(readAddr, r'\1 \2', subAddr) # For addresses with a house number, there is an nearest-intersecting street in group 3 we ignore
			kmlAddr = re.sub(readAddr, r'\1', subAddr)
			catAddr = fixedAddr + " " + "IN"
			geoResult = geocoder.arcgis(catAddr).latlng
			reverseGeo = geoResult[::-1]
			kml.newpoint(name = kmlAddr, coords = [reverseGeo])
		
kml.save(kmlSaveLoc)		

listFile.close()


		







