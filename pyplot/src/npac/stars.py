#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Utilities for SIMBAD access """
import sys
sys.path.append('../../skeletons')

import time
import urllib.request
from urllib.error import URLError, HTTPError
from collections import OrderedDict

from npac.coordinates import RaDec

from typing import Tuple

RequestCounter = 0


def format_char_for_simbad(text: str, char: str) -> str:
    """ Swap a character in a text with its Unicode code point (hexadecimal).
    Suitable only for Basic Latin as it returns only 2-digits.

    Note: the swap is preceded by %.

    See https://en.wikipedia.org/wiki/List_of_Unicode_characters

    Parameters
    ----------
    text : str
        Input text containing `char`
    char : str of size 1
        Character to be replaced by its Unicode code point

    Returns
    ----------
    out : str
        Input text with `char` replaced by its Unicode code point
        (Hexadecimal, 2-digits).

    Examples
    ----------
    >>> text = "a = 3"
    >>> char = "="

    the character = is 003D
    >>> print(format_char_for_simbad(text, char))
    a %3D 3

    Also works for multiple occurences
    >>> text = "a > 3; b > 6; c < 0"
    >>> char = ">"
    >>> print(format_char_for_simbad(text, char))
    a %3E 3; b %3E 6; c < 0

    """
    text = text.replace(char, '%{:02X}'.format(ord(char)))
    return text


def make_req(radec: RaDec, radius: float) -> str:
    """ Build a request to the Simbad server according to a RA/Dec position
    and an acceptance radius.

    Parameters
    ----------
    radec : Instance of RaDec
        Instance of RaDec. RA/Dec values are floats (degrees).
    radius : float
        Floating value of the acceptance radius (degrees)

    Returns
    ----------
    request : str
        String describing the request to Simbad.

    Examples
    ----------
    >>> radec = RaDec(1.0, 1.0)
    >>> request = make_req(radec, 0.001)

    Check we are querying the correct website
    >>> assert("http://simbad.u-strasbg.fr" in request)

    çheck that the radius value has been correctly understood, including the
    transformation of characters (see `format_char_for_simbad()`).
    >>> assert("radius%3D0.001" in request)
    """
    host_simbad = 'simbad.u-strasbg.fr'

    # WGET with the "request" string built as below :

    script = ''
    # output format (for what comes from SIMBAD)
    script += 'format object f1 "'

    # hour:minute:second
    script += '%COO(A)'

    # degree:arcmin:arcsec
    script += '\t%COO(D)'
    script += '\t%OTYPE(S)'
    script += '\t%IDLIST(1)'
    script += '\t%DIST'
    script += '"\n'

    script += 'query coo '

    # append "a_ra" (decimal degree)
    script += '{}'.format(radec.ra)
    script += ' '

    # append "a_dec" (decimal degree)
    script += '{}'.format(radec.dec)
    script += ' radius='

    # append "a_radius" (decimal degree)
    script += '{}'.format(radius)

    # d,m,s
    script += 'd'

    # fk5
    script += ' frame=FK5 epoch=J2000 equinox=2000'
    script += '\n'

    # limit return size
    script += 'set limit 100 '
    script += '\n'

    # "special characters" converted to "%02X" format :
    script = format_char_for_simbad(script, '%')
    script = format_char_for_simbad(script, '+')
    script = format_char_for_simbad(script, '=')
    script = format_char_for_simbad(script, ';')
    script = format_char_for_simbad(script, '"')
    script = format_char_for_simbad(script, ' ')

    # CR+LF
    script = script.replace('\n', '%0D%0A')
    script = format_char_for_simbad(script, '\t')

    request = 'http://' + host_simbad + '/simbad/sim-script?'
    request += 'script=' + script + '&'

    return request


def wget(req: str) -> str:
    """ Query Simbad with a request `req`.

    Parameters
    ----------
    req: str
        Request to be sent to Simbad. See `make_req`.

    Returns
    ----------
    out : str
        Results returned by Simbad to the query. Contained name, type, position
        of objects and other metadata.

    Raises
    ----------
    HTTPError
        If we cannot reach the website after 10 trials.
    URLError
        If we cannot read the URL returned by Simbad.

    Examples
    ----------
    >>> radec = RaDec(1.0, 1.0)
    >>> request = make_req(radec, 0.1)
    >>> out = wget(request)

    `out` is a pretty long message containing all the results returned
    by Simbad. Let's just check it has done its job
    >>> assert("simbatch done" in out)
    """

    global RequestCounter

    retry = 0
    result = ""

    if RequestCounter > 7:
        time.sleep(1.0)
        RequestCounter = 0
    else:
        RequestCounter += 1

    while retry < 10:
        try:
            result = urllib.request.urlopen(req)
            break
        except HTTPError:
            retry += 1
            time.sleep(1.0)
        except BaseException:
            raise

        sys.stderr.write('Retrying to read ({} attempts remaining)'.format(retry))

    if result is "":
        return ""

    try:
        text = result.read()
        text = text.decode('utf-8')
        lines = text.split('<BR>\n')
        return lines[0]
    except URLError:
        sys.stderr.write('cannot read URL {}'.format(req))
    except BaseException:
        raise


def get_celestial_objects(radec: RaDec, radius: float=0.2) -> Tuple[OrderedDict, list, str]:
    """ Retrieve only celestial objects from Simbad contained in the circle
    defined by radec and radius.

    Note that it also returns the full results returned by Simbad (not only
    celestial objects), and the initial request for further inspection.

    Parameters
    ----------
    radec : Instance of RaDec
        Instance of RaDec. RA/Dec values are floats (degrees).
    radius : float
        Floating value of the acceptance radius (degrees)

    Returns
    ----------
    objects : OrderedDict
        Celestial objects returned by Simbad to the query.
    out : List of str
        Full results returned by Simbad to the query, formatted line-by-line.
        Contained name, type, position of objects and other metadata.
    req : str
        Request sent to Simbad.

    Examples
    ----------
    >>> radec = RaDec(1.0, 1.0)
    >>> cobjects, _, _ = get_celestial_objects(radec, 0.1)

    Look a the first celestial object
    >>> vals = list(cobjects.items())
    >>> print(vals)
    [('SDSS J000355.58+005811.7', 126.98941941434539), ('SDSS J000414.22+005601.0', 320.3625022956627)]

    >>> len(vals)
    2
    """
    req = make_req(radec, radius)
    out = wget(req)
    objects = OrderedDict()

    out = out.split('\n')
    in_data = False
    raw_objects = dict()

    for line in out:
        line = line.strip()
        if line == '':
            continue
        if not in_data:
            if line == '::data::' + '::' * 36:
                in_data = True
            continue

        data = line.split('\t')
        obj_type = data[2].strip()
        obj_name = data[3].strip()
        obj_dist = data[4].strip()
        if obj_type == 'Star':
            raw_objects[obj_name] = float(obj_dist)

    # here we sort the dictionary keys (name of the star) 
    # depending on the dictionary values (distance of the star... to what ?)
    objects = OrderedDict()
    for k in sorted(raw_objects, key=raw_objects.__getitem__):
      objects[k] = raw_objects[k]
    
    return objects, out, req


def _tests():
    """ Unit tests for stars.py To run the test, execute:

    python3 stars.py

    It should exit gracefully if no error (exit code 0),
    otherwise it will print on the screen the failure.

    In PyCharm, just click on Run "Doctests in stars" button (green button),
    or CTRL+click on the file, and choose Run "Doctests in stars".
    """
    import doctest
    # radec = RaDec(1.0, 1.0)
    # cobjects, _, _ = get_celestial_objects(radec, 0.1)
    # for cobj_name in sorted(cobjects.keys()):
    #     print(cobj_name)

    doctest.testmod()


if __name__ == '__main__':
    """ Execute the test suite """
    _tests()
