# -*- coding: utf-8 -*-
""" utils.py

Utilities for Qt widgets

"""
from __future__ import division, print_function

from datetime import datetime as dt
import fnmatch
import logging
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

logger = logging.getLogger()


### Utilities
def locate_files(location, pattern):
    """ Recursively search location for files matching pattern

    Args:
      location (str): directory location to search
      pattern (str): filename pattern for fnmatch.filter

    Returns:
      files (list): full filepaths for files found in location matching pattern

    """
    files = []

    for root, dirnames, filenames in os.walk(os.path.abspath(location)):
        for filename in fnmatch.filter(filenames, pattern):
            files.append(os.path.join(root, filename))

    return files

def parse_date_from_filename(filename):
    """ Tries to extract date from a filename for common image filenames

    Should work for:
        - Landsat

    Args:
      filename (str): filename to extract from

    Returns:
      date_str (datetime): datetime object for file if parsed, else None

    """
    filename = os.path.basename(filename)
    date = None

    # Landsat filename - substring from 9 - 16 (e.g., LE70220492000037EDC00)
    date_str = filename[9:16]
    try:
        date = dt.strptime(date_str, '%Y%j')
    except:
        logger.debug('File {f} could not be parsed for date as Landsat'.format(
            f=filename))

    if not date:
        logger.warning('Could not parse date for {f}'.format(f=filename))

    return date


### Validators
def gdal_file_validator(f):
    """ Validate a file is openable by GDAL as read-only

    Args:
      f (str): filename to validate

    Raises:
      ImportError: raised if GDAL can't be imported
      RuntimeError: raised if file can't be opened

    """
    from osgeo import gdal
    gdal.UseExceptions()
    gdal.AllRegister()

    ds = gdal.Open(f, gdal.GA_ReadOnly)
    ds = None


### Slots
def find_file(edit_name, validator,
              dialog_text=None,
              location=None, extension='',
              raise_exception=False):
    """ File browsing slot

    Ties together a "Browse" QPushButton with a corresponding QLineEdit.
    Changes the text of the QLineEdit if the validator function comes back
    successful.

    Args:
      edit_name (QLineEdit): field for name of file
      validator (function): validation function
      dialog_text (str, optional): dialog window text
      location (str, optional): location to open file browser
      extension (str, optional): file extension for filtering
      raise_exception (bool, optional): raise exception on validation failure

    Returns:
      filename (str): filename chosen by user, or current value if user
        cancels or the file chosen does not validate

    """
    if not dialog_text:
        dialog_text = 'Locate file'

    if not location:
        if edit_name.text() == '':
            location = os.getcwd()
        else:
            location = edit_name.text()

    # Open file browser
    f = QtGui.QFileDialog.getOpenFileName(
            edit_name,
            dialog_text,
            location,
            extension)

    f = str(f)

    try:
        success = validator(f)
    except:
        logger.error('Could not validate file {f}'.format(f=f))
        if raise_exception:
            raise
        return edit_name.text()

    edit_name.setText(f)
    return f
