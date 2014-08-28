# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ImageComposite
                                 A QGIS plugin
 Multi-date image composite algorithms implemented in QGIS
                              -------------------
        begin                : 2014-08-25
        git sha              : $Format:%H$
        copyright            : (C) 2014 by Chris Holden
        email                : ceholden@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import division, print_function

from datetime import datetime as dt
import fnmatch
from functools import partial
import logging
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

from osgeo import gdal

from ui_main_compositor import Ui_ImageCompositor as Ui_Dialog

from utils import (gdal_file_validator, find_file, locate_files,
                   parse_date_from_filename)

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=logging.DEBUG,
                            datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

class CompositorDialog(QtGui.QDialog, Ui_Dialog):

    # Store
    images_added = []

    def __init__(self, iface):

        QtGui.QDialog.__init__(self)
        self.iface = iface
        self.setupUi(self)

        self.setup_gui()

    def setup_gui(self):
        """ Binds signals to slots and initializes GUI elements """
        # "Add Images" or "Import Directory"
        self.groupbox_importer.setAlignment(QtCore.Qt.AlignHCenter)
        self.rbut_image.setChecked(True)
        self.rbut_dir.setChecked(False)
        self.stackwidget_importer.setCurrentIndex(
            0 if self.rbut_image.isChecked() else 1)

        self.rbut_image.toggled.connect(self.importer_changed)
        self.rbut_dir.toggled.connect(self.importer_changed)

        # Disable add and import buttons because they start with no text
        self.but_imageadd.setEnabled(False)
        self.but_dirimport.setEnabled(False)

        # Image import - image by image
        self.but_imagebrowse.clicked.connect(
            partial(find_file,
                    self.edit_imagename,
                    gdal_file_validator))

        self.edit_imagename.textChanged.connect(
            partial(self.enable_import_buttons,
                    self.but_imageadd, [self.edit_imagename]))

        # Image import - images matching pattern within directory
        self.but_dirbrowse.clicked.connect(self.import_directory)
        self.but_dirimport.clicked.connect(self.import_directory_images)

        self.edit_dirname.textChanged.connect(
            partial(self.enable_import_buttons,
                    self.but_dirimport,
                    [self.edit_dirname, self.edit_imagepattern]))
        self.edit_imagepattern.textChanged.connect(
            partial(self.enable_import_buttons,
                    self.but_dirimport,
                    [self.edit_dirname, self.edit_imagepattern]))

    def add_images(self, images):
        """ Adds images to table

        Args:
          image (list): images to be added to table

        """
        if isinstance(images, str):
            images = [images]

        for image in images:
            # Try to get date
            date = parse_date_from_filename(image)
            if date is None:
                date = 'None'
            else:
                date = date.strftime('%x')

            # Validate?

            self.images_added.append((os.path.basename(image),
                                      date))

        self.update_table()


    def update_table(self):
        """ Synchronizes self.images_added with the table """
        print(self.images_added)



# Slots
    @QtCore.pyqtSlot(bool)
    def importer_changed(self, bool):
        """ Change the index of stack widget based on radio button status """
        self.stackwidget_importer.setCurrentIndex(
            0 if self.rbut_image.isChecked() else 1)

    @QtCore.pyqtSlot(QtGui.QPushButton, list, QtCore.QString)
    def enable_import_buttons(self, button, edits, text):
        """ Enables button if the QLineEdits in [edits] have text """
        enable = [False] * len(edits)
        for i, edit in enumerate(edits):
            if str(edit.text()) != '':
                enable[i] = True

        button.setEnabled(all(enable))

    @QtCore.pyqtSlot()
    def import_directory(self):
        """ Opens a QFileDialog to find a directory """
        # Determine default location - os.getcwd if nothing already selected
        location = self.edit_dirname.text()
        if not os.path.isdir(location):
            location = os.getcwd()

        selected = QtGui.QFileDialog.getExistingDirectory(
            self,
            'Select a directory to import',
            location,
            QtGui.QFileDialog.ShowDirsOnly)

        if selected:
            self.edit_dirname.setText(selected)

    @QtCore.pyqtSlot()
    def import_directory_images(self):
        """ Tries to import images from a directory

        Images need to have the same number of band and same projection.

        """
        # Find files matching pattern
        location = str(self.edit_dirname.text())
        pattern = str(self.edit_imagepattern.text())

        images = locate_files(location, pattern)

        # Validate that we can open them
        for image in images:
            try:
                ds = gdal.Open(image, gdal.GA_ReadOnly)
                ds = None
            except:
                logger.warning('Cannot open {i}'.format(i=image))
                images.remove(image)

        self.add_images(images)

    def unload(self):
        """ Unloads resources """

# main for testing
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = CompositorDialog(app)
    window.show()
    sys.exit(app.exec_())
