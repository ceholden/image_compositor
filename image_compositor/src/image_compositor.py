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
from PyQt4 import QtCore
from PyQt4 import QtGui
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from compositor_dialog import CompositorDialog
import os


class ImageComposite:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """ Initialize plugin

        :param iface: An interface instance that will be passed to this class
            which provides th

        :param iface: An interface instance that will be passed to this class
            which e hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QtCore.QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'ImageComposite_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QtCore.QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QtCore.QCoreApplication.installTranslator(self.translator)

        # Create dialog and keep reference
        self.dlg = CompositorDialog(self.iface)

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/image_compositor/resources/icon.png'

        self.show_dialog = QtGui.QAction(
            QtGui.QIcon(icon_path),
            'Produce image composites',
            self.iface.mainWindow())
        self.show_dialog.triggered.connect(self.show_plugin_dialog)
        self.iface.addToolBarIcon(self.show_dialog)

    def show_plugin_dialog(self):
        """ Show dialog window """
        self.dlg.show()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        # Remove toolbar
        self.iface.removeToolBarIcon(self.show_dialog)

        # Disconnect signals
        self.show_dialog.triggered.disconnect()

        self.dlg.unload()
        self.dlg.close()
        self.dlg = None

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
