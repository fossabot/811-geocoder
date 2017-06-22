# -*- coding: UTF-8 -*-

######################################################################################
# Locate Geocoder with KML writing                                                   #
# Feed in a CSV, receive KML Long/Lat                                                #
# Author: Stephan Garland, Carroll White REMC                                        #
# Shoutout to Geocod.io for having the best address normalizer I have ever seen      #
# Directions: Create a CSV that has a header named Address, containing the address   #
#                                                                                    #
#             Run the script, import the KML into ArcEarth with your territory KML   #
######################################################################################

import csv
import json
import time
import simplekml
import shapely
import string

# For quick and easy GUI, I'm informing the user with pymsgbox, and getting files with tkinter
import pymsgbox.native as gui

import pandas as pd

try:
    from tkinter import Tk as tk  # Python 3.x
    from tkinter.filedialog import askopenfilename as getFile
    from tkinter.filedialog import asksaveasfilename as saveFile

except ImportError:  # Python 2.x
    from Tkinter import Tk as tk
    from tkFileDialog import askopenfilename as getFile
    from tkFileDialog import asksaveasfilename as saveFile

from geocodio import GeocodioClient
from shapely.geometry import Point, shape
from os import remove
from sys import version_info
from time import strftime
from xlsxwriter.utility import xl_rowcol_to_cell



def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)



def printToLog(inputText):
    textToPrint = inputText
    print(textToPrint)
    with open(logFile, 'a') as log:
        log.write(textToPrint)



# Does a simple bounding check to see if the plotted point is roughly in our area
def boundsCheck(x, y):
    failString = "\n***** " + kmlAddr + " failed sanity check, manually check territory *****"
    # Negative check because otherwise the positive matches wouldn't get printed
    if not (abs(floatGeoLat) > geoLatMax or abs(floatGeoLong) > geoLongMax or abs(floatGeoLat) < geoLatMin or abs(floatGeoLong) < geoLongMin):
        print("\n" + kmlAddr + " correctly mapped.")
        # Moved the plotting into the function so out-of-bounds are only logged in the text file
        kml.newpoint(name = kmlAddr, coords = [reverseGeo])
    else:
        printToLog(failString)



# Allows user to quit at any time throughout GUI input
def killProgram(cancel):
    if cancelSel == 'Cancel':
        gui.alert("Goodbye!")
        quit()
    else:
        pass
        


def getInput(question, type):
    while True:
        try:
            return type(gui.prompt(question))
        except Exception: # Loop if they don't input correct type
            pass
        else:
            gui.alert("Goodbye!")
            quit()
            
   

def jsonRead(input):
    global jsonFile
    point = Point(reverseGeo)
    with open(jsonFile, 'r') as jsonFile:
        js = json.load(jsonFile)
    
    for feature in js['features']:
            polygon = shape(feature['geometry'])
            territoryOwner = str(feature['properties']['NAME_ABREV'])
            if (polygon.contains(point)) \
            and str(feature['properties']['NAME_ABREV'] == "CWREMC"):       
                print(str(kmlAddr) + " is in our territory. ID is " + str(feature['properties']['OBJECTID']))
            else:
                print(str(kmlAddr) + " is not in our territory; owned by " + territoryOwner)
                
                with open(inCSV, 'r') as inFile:
                    reader = csv.DictReader(inFile, delimiter = ',', quotechar = '"')
               
                    with open(outCSV, 'w') as out:
                        fieldnames = ['Request No', 'Address', 'Owner']
                        writer = csv.DictWriter(out, delimiter = ',', quotechar = '"', fieldnames = reader.fieldnames)
                        writer.writeheader()
                        for row in reader:
                            if row == "request no":
                                writer.writerow(row)
                                writer.writerow({'Request No': row['request no'], 'Address': row['address'], 'Owner': "territoryOwner"})
                


def pandasOutput(input):
    df = pd.read_csv(outCSV)
    header = ['Request No', 'Address', 'Owner']

    writer = pd.ExcelWriter(outExcel, engine = 'xlsxwriter')

    df.to_excel(writer, index = False, sheet_name = 'Sheet1', columns = header)

    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    worksheet.set_column('A:A', 15)
    worksheet.set_column('B:B', 45)
    worksheet.set_column('C:C', 15)

    writer.save()
        
    os.remove(outCSV)



apiKey = getInput("Please enter your Geocodio API Key", str)
gc = GeocodioClient(apiKey)

outCSV = 'P:/Out_CSV.csv'
outExcel = 'P:/Test_Output.xlsx'

root = tk()
# Hides the TK background window
root.withdraw()

cancelSel = gui.confirm("Please select your Territory GeoJSON file", "GeoJSON Location", ['OK', 'Cancel'])
killProgram(cancelSel)

# Select the territory GeoJSON file
if version_info.major == 2:
# Python 2.x wants the default as the last item. Python 3.x wants it as the first.
    jsonFile = getFile(title = "Territory Location",
                      filetypes = (("All Files", "*.*"),("GeoJSON", "*.geojson")))
else:
    jsonFile = getFile(title = "Territory Location",
                      filetypes = (("GeoJSON", "*.geojson"),("All Files", "*.*")))

try:
    # pymsgbox literally interprets indentation, hence the non-indented continue line
    cancelSel = gui.confirm("Enter your rough territory coordinates in unsigned decimal \
format, e.g. 87.152. Use at least four significant figures.", "Coordinate entry", ['OK', 'Cancel']) 
    killProgram(cancelSel)
    # absolute value in case instructions are ignored
    geoLatMin = abs(float(getInput("Please enter your southernmost point", float)))
    geoLatMax = abs(float(getInput("Please enter your northernmost point", float)))
    geoLongMin = abs(float(getInput("Please enter your easternmost point", float)))
    geoLongMax = abs(float(getInput("Please enter your westernmost point", float)))
except AttributeError:
    gui.alert("Goodbye!")
    quit()

orgName = getInput("Please enter your organization's name", str)

# upper() probably isn't required for Geocodio, but the rest of the address is all caps, so...
stateVar = getInput("Please enter the two-digit code for your state", str).upper()
# checks for length of two, and also that input is in upper/lowercase ascii letter set
while not len(stateVar) == 2 or len(sorted(set(stateVar).difference(string.ascii_letters))) > 0: 
    stateVar = getInput("Please enter the two-digit code for your state", str).upper()
else:
    pass

cancelSel = gui.confirm("Please select your CSV", "CSV Location", ['OK', 'Cancel'])
killProgram(cancelSel)

# Select the input CSV file
if version_info.major == 2:
# Python 2.x wants the default as the last item. Python 3.x wants it as the first.
    inCSV = getFile(title = "CSV Location",
                      filetypes = (("All Files", "*.*"),("CSV", "*.csv")))
else:
    inCSV = getFile(title = "CSV Location",
                      filetypes = (("CSV", "*.csv"),("All Files", "*.*")))

cancelSel = gui.confirm("Please select the logfile save location and filename",
                        "Log Location", ['OK', 'Cancel'])
killProgram(cancelSel)

# Select the logfile save location
if version_info.major == 2:
    logFile = saveFile(
                       parent = root,title = "Log Location",
                       initialfile = strftime("%Y-%m-%d - ") + orgName + ' - Geocoder Log.txt',
                       filetypes = (("All Files", "*.*"),("Text", "*.txt")))
else:
    logFile = saveFile(
                       parent = root,title = "Log Location",
                       initialfile = strftime("%Y-%m-%d - ") + orgName + ' - Geocoder Log.txt',
                       filetypes = (("Text", "*.txt"),("All Files", "*.*")))

# Opens, nulls, and closes the logfile for each run
open(logFile, 'w').close()

kml = simplekml.Kml()
cancelSel = gui.confirm("Please select the KML save location and filename",
                        "KML Location", ['OK', 'Cancel'])
killProgram(cancelSel)

# Select the KML save location
if version_info.major == 2:
    kmlSaveLoc = saveFile(
                          parent = root,title = "KML Location",
                          initialfile = strftime("%Y-%m-%d - ") + orgName + ' - Geocoding Results.kml',
                          filetypes = (("All Files", "*.*"),("KML","*.kml")))
else:
    kmlSaveLoc = saveFile(
                          parent = root,title = "KML Location",
                          initialfile = strftime("%Y-%m-%d - ") + orgName + ' - Geocoding Results.kml',
                          filetypes = (("KML","*.kml"),("All Files", "*.*")))

# Python 2.7 throws an insecure platform warning, and urllib3 doesn't install on ESRI's 2.7 distro.
# The warnings clutter up stdout, so they're suppressed.
try:
    import urllib3.contrib.pyopenssl
    urllib3.contrib.pyopenssl.inject_into_urllib3()
except ImportError:
    import requests
    from requests.packages.urllib3.exceptions import InsecurePlatformWarning
    requests.packages.urllib3.disable_warnings()

start_time = time.time()
printToLog("Start: " + strftime("%Y-%m-%d %H:%M:%S") + "\n")

with open(inCSV,'r') as inFile:
    reader = csv.DictReader(inFile, delimiter = ',', quotechar = '"')
    
    for row in reader:    
        # Cat address and defined state for geocoding
        catAddr = row['address'] + " " + stateVar
        kmlAddr = row['address'] # used for printing to fail log
        
        # Run above list through Geocodio, return coords in Lat/Long
        geoResult = gc.geocode(catAddr).coords
        
        # I had to either append [::-1] to the above to reverse it inline, or do so later.
        # I need to cut out the Long/Lat in the next two for boundary checks.
        # I decided this way was easier to read, albeit not as compact.
        reverseGeo = geoResult[::-1]
        
        # Slice the string into two parts, cast it to a string, then to a float to compare.
        # Yes, this is horrendously ugly.         
        floatGeoLong = float(str(reverseGeo[1:]).replace('(','').replace(')','').replace(',',''))
        floatGeoLat = float(str(reverseGeo[:1]).replace('(','').replace(')','').replace(',',''))

        # Simple sanity check for service territory; if valid, plots location
        boundsCheck(floatGeoLong, floatGeoLat)
        # Feeds each geocoded spot into automated checker
        jsonRead(reverseGeo)

# Takes jsonInput()'s CSV file (points not owned), generates an Excel file via pandas, deletes CSV
pandasOutput(outCSV)
        
end_time = time.time()
printToLog("\n\nEnd: " + strftime("%Y-%m-%d %H:%M:%S"))
printToLog("\n\nIt took {} to execute this script.".format(hms_string(end_time - start_time)))

kml.save(kmlSaveLoc)

gui.alert("Please see the logfile, located at\n" + logFile + " \nfor any failed geocodes.", 'Program Complete')
