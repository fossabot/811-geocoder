Dependencies:
*************

* `Geocoder <https://pypi.python.org/pypi/geocoder>`_
* `SimpleKML <https://pypi.python.org/pypi/simplekml/>`_

**Optional for 2.7.x:**

* `urllib3 <https://pypi.python.org/pypi/urllib3>`_

How to use 811-geocoder:
************************
1. Create a CSV containing the addresses you wish to plot, under a header named Address. Anything else contained in the CSV will be ignored.

2. The parsing is based on a simple regex that is setup for USIC's naming scheme, which is one of the two cases:

* $HOUSE_NUM $STREET_NAME $TOWN $NEAREST_INTERSECTION
* $INTERSECTING_STREET_1_NAME $TOWN $INTERSECTING_STREET_2_NAME	

3. Run the script after setting variables file and kmlSaveLoc to your desired path.

4. This will create a kml containing a named map location for every input.

5. Import the kml into your preferred imagery program, along with an overlay of service territories.

Noted shortcomings:
*******************

* Does not have sanity check for out-of-bounds. Some addresses will geocode into distant lands. If you get a dot in Antarctica, there's a good chance it didn't work. Upcoming version will at the very least note these.

* Does not show status while performing geocodes. It's currently setup to use ArcGIS' free service, which allows a single address at a time. Other providers allow batch geocodes with an API key. Again, a status update is forthcoming.



