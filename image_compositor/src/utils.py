# -*- coding: utf-8 -*-
""" utils.py

Utilities for Qt widgets

"""
from __future__ import division, print_function

import logging
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

logger = logging.getLogger()


### Validators
def gdal_file_validator(f):
    """ Validate a file is openable by GDAL as read-only

    Args:
      f (string)                        filename to validate

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

