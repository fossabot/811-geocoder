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

3. Run the script after setting bounding box checks to your coordinates.

4. This will create a kml containing a named map location for every input.

5. Import the kml into your preferred imagery program, along with an overlay of service territories.


Changelog:
**********

* v1.0 - Initial release. It works.
* v1.1 - Does sanity checks for the area, implements logging for any that appear to be wildly wrong, and shows status.
* v1.2 - Includes basic GUI (tkinter and pymsgbox), is 2.x/3.x compatible, and allows user to kill program through GUI.

Noted shortcomings:
*******************

* Doesn't do automated checking. This may occur in a future version, probably using a JSON conversion for territories and Shapely's polygon.contains()


