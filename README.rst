[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FstephanGarland%2F811-geocoder.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2FstephanGarland%2F811-geocoder?ref=badge_shield)

Dependencies:
*************

* `Geocodio <https://pypi.python.org/pypi/geocodio>`_
* `Pandas <https://pypi.python.org/pypi/pandas>`_
* `Shapely <https://pypi.python.org/pypi/Shapely>`_
* `SimpleKML <https://pypi.python.org/pypi/simplekml/>`_

**Optional for 2.7.x:**

* `urllib3 <https://pypi.python.org/pypi/urllib3>`_

How to use 811-geocoder:
************************
1. Create a CSV containing the addresses you wish to plot, and request numbers - column names "request no" and "address".

2. Address normalization is handled entirely by the geocoder.

3. Run the script after setting bounding box checks to your coordinates.

4. This will create a kml containing a named map location for every input.

5. Import the kml into your preferred imagery program, along with an overlay of service territories.

6. View the created Excel file for any out-of-bounds addresses, for manual verification.


Changelog:
**********

* v1.0 - Initial release. It works.
* v1.1 - Does sanity checks for the area, implements logging for any that appear to be wildly wrong, and shows status.
* v1.2 - Includes basic GUI (tkinter and pymsgbox), is 2.x/3.x compatible, and allows custom entry of territory boundaries.
* v1.3 - Changed to geocodio from geocoder, got rid of regex address matching, using pandas internally.
* v1.4 - Uses shapely to generate point-in-polygon checks, includes more input checks, removed default coordinates.

Noted shortcomings:
*******************

* Point-in-polygon isn't perfect. It is helpful, but you will need to check its output for sanity.




## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2FstephanGarland%2F811-geocoder.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2FstephanGarland%2F811-geocoder?ref=badge_large)