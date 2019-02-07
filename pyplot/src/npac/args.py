#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""args module"""
import argparse
import os
import sys

from typing import Tuple

def get_default_data_path() -> str:
    """ Etablish the default path and file values

    Returns
    ---------
    default_data_path : str
        Default path to the data.

    Examples
    ---------
    >>> get_default_data_path()
    '../../../data/fits'
    """
    default_data_path = os.environ.get('DATAPATH')

    # Should be better handled... Why not having a recursive routine
    # with an exception if not found?
    if default_data_path is None:
        if os.path.exists('../../../data/fits'):
            default_data_path = '../../../data/fits'
        elif os.path.exists('../../data/fits'):
            default_data_path = '../../data/fits'
        elif os.path.exists('../data/fits'):
            default_data_path = '../data/fits'
        elif os.path.exists('../data'):
            default_data_path = '../data'
        else:
            sys.stderr.write('No default data path found!')
            exit(1)

    return default_data_path


def get_args() -> Tuple[str, bool]:
    """ Analyse the command line arguments using argparse
    If the mode of execution is interactive, you'll be asked to provide
    an input file name.

    Returns
    ---------
    data_file : str
        Name (including path) of the input FITS file.
    isInteractive : bool, optional
        True if we are working interactively. False otherwise.
        Default is True (and should be unless you know what you are doing).

    Raises
    ---------
    FileNotFoundError
        If the input file is not found.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-b',
        dest='batch',
        action='store_true',
        default=False,
        help='batch mode, no graphics and no interaction')
    parser.add_argument('file', nargs='?', type=str, help='fits input file')
    args = parser.parse_args()

    if not args.file:
        # if no file name given on the command line
        default_data_file = 'common'
        if args.batch:
            data_file = default_data_file
        else:
            data_file = input('file name [%s]? ' % default_data_file)
            if not data_file:
                data_file = default_data_file
    else:
        data_file = args.file

    if not data_file.endswith('.fits'):
        # we need *.fits files
        data_file += '.fits'

    if data_file.rfind('/') == -1 and data_file.rfind('\\') == -1:
        # when an explicit path is not provided, prepend the default path
        data_file = get_default_data_path() + '/' + data_file

    if not os.path.exists(data_file):
        raise FileNotFoundError(
            'Image file ({}) not found'.format(data_file))

    # we don't test if the file actually exists.
    # thus we expect that this test will occur at open time (perhaps using a
    # try clause)

    return data_file, not args.batch

def _tests():
    """ Unit tests for args.py To run the test, execute:

    python3 args.py

    It should exit gracefully if no error (exit code 0),
    otherwise it will print on the screen the failure.

    In PyCharm, just click on Run "Doctests in args" button (green button),
    or CTRL+click on the file, and choose Run "Doctests in args".
    """
    import doctest
    doctest.testmod()


if __name__ == '__main__':
    """ Execute the test suite """
    _tests()
