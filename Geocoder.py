# -*- coding: UTF-8 -*-

######################################################################################
# Locate Geocoder with KML writing                                                   #
# Feed in a CSV, receive KML Long/Lat                                                #
# Author: Stephan Garland, Carroll White REMC                                        #
# Shoutout to Wiktor Stribiżew on StackOverflow for the regex                        #
# Directions: Create a CSV that has a header named Address, containing the address   #
#             The regex is setup for USIC's naming scheme for addresses:             #
#             $HOUSE_NUM $STREET_NAME $TOWN $NEAREST_INTERSECTION                    #
#             $INTERSECTING_STREET_1_NAME $TOWN $INTERSECTING_STREET_2_NAME          #
#             Run the script, import the KML into ArcEarth with your territory KML   #
#             TODO: Point-in-polygon, maybe                                          #
######################################################################################

import csv
import re
import time
import geocoder
import simplekml

# For quick and easy GUI, I'm informing the user with pymsgbox, and getting files with tkinter
import pymsgbox.native as gui

try:
    from tkinter import Tk as tk  # Python 3.x
    from tkinter.filedialog import askopenfilename as getFile
    from tkinter.filedialog import asksaveasfilename as saveFile

except ImportError:  # Python 2.x
    from Tkinter import Tk as tk
    from tkFileDialog import askopenfilename as getFile
    from tkFileDialog import asksaveasfilename as saveFile

from sys import version_info
from time import strftime


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
# Change the coordinates to whatever area you need, or comment it out
def boundsCheck(x, y):
    failString = "\n***** " + kmlAddr + " failed sanity check, manually check territory *****"
    # Negative check because otherwise the positive matches wouldn't get printed
    if not (abs(floatGeoLat) > 41.07 or abs(floatGeoLong) > 87.152 or abs(floatGeoLat) < 40.418 or abs(floatGeoLong) < 86.18):
        print("\n" + kmlAddr + " correctly mapped.")
    else:
        printToLog(failString)


# Allows user to quit at any time throughout GUI input
def killProgram(cancel):
    if cancelSel == 'Cancel':
        print("User quit!")
        time.sleep(3)
        quit()
    else:
        pass

        
cancelSel = gui.confirm("Please enter your organization's name ", "Organization", ['OK', 'Cancel'])
killProgram(cancelSel)

try:
    orgName = raw_input("Organization: ")  # Python 2.x
except NameError:
    orgName = input("Organization: ")  # Python 3.x

cancelSel = gui.confirm("Please enter the two-digit code for your state", "Select state", ['OK', 'Cancel'])
killProgram(cancelSel)

try:
    stateVar = raw_input("State: ").upper()  # Python 2.x
except NameError:
    stateVar = input("State: ").upper()  # Python 3.x

cancelSel = gui.confirm("Please select your CSV", "CSV Location", ['OK', 'Cancel'])
killProgram(cancelSel)

root = tk()
# Hides the TK background window
root.withdraw()

# Select the input CSV file
if version_info.major == 2:
# Python 2.x wants the default as the last item. Python 3.x wants it as the first.
    csvFile = getFile(title = "CSV Location",
                      filetypes = (("All Files", "*.*"),("CSV", "*.csv")))
else:
    csvFile = getFile(title = "CSV Location",
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

with open(csvFile,'r') as listFile:
    reader = csv.DictReader(listFile, delimiter = ',', quotechar = '"')

    for row in reader:
        testAddr = row['Address']
        if not testAddr[:1].isdigit():
            # If the address doesn't start with a number, it's an intersection.
            # Regex: \s+ - whitespace character[1-inf, greedy]; \S+ - non-whitespace character[1-inf, greedy].
            #        \s* - whitespace character[0-inf, greedy]; (.*) - any character.

            # Pull the non-parsed address out, which will include the city.
            # Note, breaking line after pipe will cause regex to fail (e.g. Street|\).
            readAddr = re.compile(\
                                  r"(Avenue|Lane|Road|Court|Boulevard|Drive|Street\
                                  |Ave|Dr|Rd|Ct|Blvd|Ln|St)\s+(\S+)\s*(.*)", re.I)
            subAddr = row['Address']

            # Run it through the regex, group it as 1 & 3 2, which generates an intersection and city
            fixedAddr = re.sub(readAddr, r'\1 & \3 \2', subAddr)
            
            # For tagging the map point, ignore the city to save space on map
            kmlAddr = re.sub(readAddr, r'\1 & \3', subAddr)
            
            # Cat address and defined state for geocoding
            catAddr = fixedAddr + " " + stateVar
            
            # Run above list through ArcGIS via geocoder, and save as Lat/Long
            geoResult = geocoder.arcgis(catAddr).latlng
            
            # I had to either append [::-1] to the above to reverse it inline, or do so later.
            # I need to cut out the Long/Lat in the next two for boundary checks.
            # I decided this way was easier to read, albeit not as compact.

            # Slice the string into two parts, cast it to a string, then to a float to compare.
            # Yes, this is horrendously ugly.         
            floatGeoLong = float(str(geoResult[1:]).replace('[','').replace(']',''))
            floatGeoLat = float(str(geoResult[:1]).replace('[','').replace(']',''))

            # Simple sanity check for service territory
            boundsCheck(floatGeoLong, floatGeoLat)

            # simplekml needs Long/Lat, and reversed() wasn't working, so slice the list
            reverseGeo = geoResult[::-1]

            kml.newpoint(name=kmlAddr, coords=[reverseGeo])
        else:
            # Otherwise, assume it has a street number
            readAddr = re.compile(\
                                  r"(Avenue|Lane|Road|Court|Boulevard|Drive|Street\
                                  |Ave|Dr|Rd|Ct|Blvd|Ln|St)\s+(\S+)\s*(.*)", re.I)
            subAddr = row['Address']

            # For addresses with a house number, there is an nearest-intersecting street in group 3 we ignore
            fixedAddr = re.sub(readAddr, r'\1 \2', subAddr)
            kmlAddr = re.sub(readAddr, r'\1', subAddr)

            catAddr = fixedAddr + " " + stateVar

            geoResult = geocoder.arcgis(catAddr).latlng

            floatGeoLong = float(str(geoResult[1:]).replace('[','').replace(']',''))
            floatGeoLat = float(str(geoResult[:1]).replace('[','').replace(']',''))

            boundsCheck(floatGeoLong, floatGeoLat)
            reverseGeo = geoResult[::-1]

            kml.newpoint(name = kmlAddr, coords = [reverseGeo])

end_time = time.time()
printToLog("\n\nEnd: " + strftime("%Y-%m-%d %H:%M:%S"))
printToLog("\n\nIt took {} to execute this script.".format(hms_string(end_time - start_time)))

kml.save(kmlSaveLoc)

gui.alert("Please see the logfile, located at\n" + logFile + " \nfor any failed geocodes.", 'Program Complete')
