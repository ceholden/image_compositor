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

from functools import partial
import logging
import os

from PyQt4 import QtCore
from PyQt4 import QtGui

from ui_main_compositor import Ui_ImageCompositor as Ui_Dialog

from utils import gdal_file_validator, find_file

logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s',
                            level=logging.DEBUG,
                            datefmt='%H:%M:%S')
logger = logging.getLogger(__name__)

class CompositorDialog(QtGui.QDialog, Ui_Dialog):

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

        # Image import - image by image
        self.but_imagebrowse.clicked.connect(
            partial(find_file,
                    self.edit_imagename,
                    gdal_file_validator))

        # Image import - images matching pattern within directory


# Slots
    @QtCore.pyqtSlot(bool)
    def importer_changed(self, bool):
        """ Change the index of stack widget based on radio button status """
        self.stackwidget_importer.setCurrentIndex(
            0 if self.rbut_image.isChecked() else 1)

    def unload(self):
        """ Unloads resources """

# main for testing
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    window = CompositorDialog(app)
    window.show()
    sys.exit(app.exec_())
