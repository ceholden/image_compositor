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
    added_images = []
    added_dates = []

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
        self.but_imageadd.clicked.connect(self.import_image)

        self.but_imagebrowse.clicked.connect(
            partial(find_file,
                    self.edit_imagename,
                    gdal_file_validator))

        self.edit_imagename.textChanged.connect(
            partial(self.enable_import_buttons,
                    self.but_imageadd, [self.edit_imagename]))

        # Image import - images matching pattern within directory
        self.but_dirbrowse.clicked.connect(self.open_directory)
        self.but_dirimport.clicked.connect(self.import_directory_images)

        self.edit_dirname.textChanged.connect(
            partial(self.enable_import_buttons,
                    self.but_dirimport,
                    [self.edit_dirname, self.edit_imagepattern]))
        self.edit_imagepattern.textChanged.connect(
            partial(self.enable_import_buttons,
                    self.but_dirimport,
                    [self.edit_dirname, self.edit_imagepattern]))

        # Image table widget - 3 columns so we can have stretch on 0 and
        #     interactive for 1
        self.table_images.setHorizontalHeaderLabels(['Name', 'Date', ''])
        self.table_images.horizontalHeader().setResizeMode(
            0, QtGui.QHeaderView.Stretch)
        self.table_images.horizontalHeader().setResizeMode(
            1, QtGui.QHeaderView.Interactive)
        self.table_images.hideColumn(2)

        # Remove button
        self.but_removeselected.clicked.connect(self.remove_images)

    def add_images(self, images):
        """ Adds images to table

        Args:
          image (list): images to be added to table

        """
        if isinstance(images, str):
            images = [images]

        to_add_image = []
        to_add_date = []

        for image in images:
            # Try to get date
            date = parse_date_from_filename(image)

            # Validate?

            # Make sure isn't already in table
            if image not in self.added_images:
                to_add_image.append(image)
                to_add_date.append(date)
            else:
                logger.info('Already added {i}'.format(i=image))

        # Sort before adding
        to_add_date, to_add_image = zip(*sorted(zip(to_add_date,
                                                    to_add_image)))

        self.added_images.extend(to_add_image)
        self.added_dates.extend(to_add_date)

        self.update_table(to_add_image, to_add_date)


    def update_table(self, images, dates):
        """ Adds new images to table """
        # Add new rows
        self.table_images.setRowCount(len(self.added_images))
        # Figure out where to start with new "images"
        start = len(self.added_images) - len(images)

        for row, image, date in zip(xrange(start, len(self.added_images)),
                                      images, dates):
            _image = QtGui.QTableWidgetItem(os.path.basename(image))
            _image.setFlags(QtCore.Qt.ItemIsEnabled |
                            QtCore.Qt.ItemIsSelectable)
            _image.setTextAlignment(QtCore.Qt.AlignHCenter |
                                    QtCore.Qt.AlignVCenter)

            _date = QtGui.QTableWidgetItem('None' if date is None else
                                           date.strftime('%x'))
            _date.setFlags(QtCore.Qt.ItemIsEnabled |
                           QtCore.Qt.ItemIsSelectable |
                           QtCore.Qt.ItemIsEditable)
            _date.setTextAlignment(QtCore.Qt.AlignHCenter |
                                   QtCore.Qt.AlignVCenter)

            self.table_images.setItem(row, 0, _image)
            self.table_images.setItem(row, 1, _date)


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
    def import_image(self):
        """ Import a single image specified at a time """
        filename = os.path.abspath(str(self.edit_imagename.text()))

        self.add_images([filename])

    @QtCore.pyqtSlot()
    def open_directory(self):
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

    @QtCore.pyqtSlot()
    def remove_images(self):
        """ Remove images highlighted in the table """
        selected = self.table_images.selectedItems()
        rows = set()
        for item in selected:
            rows.add(item.row())

        self.table_images.selectionModel().clearSelection()

        for row in sorted(rows, reverse=True):
            logger.debug('Removing {f}'.format(f=self.added_images[row]))
            del self.added_images[row]
            del self.added_dates[row]
            self.table_images.removeRow(row)

    def unload(self):
        """ Unloads resources """

# main for testing
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = CompositorDialog(app)
    window.show()
    sys.exit(app.exec_())
