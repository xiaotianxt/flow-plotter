# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FlowPlotterDockWidget
                                 A QGIS plugin
 Draw a plot for feature selected.
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2024-11-07
        git sha              : $Format:%H$
        copyright            : (C) 2024 by xiaotianxt
        email                : tianyp@pku.edu.cn
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

import os
import numpy as np
import matplotlib

matplotlib.use("Agg")
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtCore import pyqtSignal
from qgis.core import QgsMapLayerProxyModel, QgsFeature
from qgis.gui import QgsMapLayerComboBox, QgsFeaturePickerWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "flow_plotter_dockwidget_base.ui"))


class FlowPlotterDockWidget(QtWidgets.QDockWidget, FORM_CLASS):
    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(FlowPlotterDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://doc.qt.io/qt-5/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.init_plot()
        self.init_layer_selector()
        self.init_feature_listener()

    def init_plot(self):
        layout = self.verticalLayout  # Use the layout defined in the .ui file

        static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        static_canvas.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        static_canvas.updateGeometry()

        layout.addWidget(NavigationToolbar(static_canvas, self))
        layout.addWidget(static_canvas)

        self._static_ax = static_canvas.figure.subplots()
        t = np.linspace(0, 10, 10)
        self._static_ax.plot(t, np.tan(t), ".")

    def init_layer_selector(self):
        self.layer_selector = QgsMapLayerComboBox(self)
        self.layer_selector.setFilters(QgsMapLayerProxyModel.VectorLayer)
        self.verticalLayout.addWidget(self.layer_selector)

    def init_feature_listener(self):
        self.feature_picker = QgsFeaturePickerWidget(self)
        self.feature_picker.setLayer(self.layer_selector.currentLayer())
        self.verticalLayout.addWidget(self.feature_picker)

        self.layer_selector.layerChanged.connect(self.on_layer_changed)
        self.feature_picker.featureChanged.connect(self.on_feature_changed)

    def on_layer_changed(self, layer):
        self.feature_picker.setLayer(layer)

    def on_feature_changed(self, feature: QgsFeature):
        print(feature)
        if feature and feature.isValid():
            QtWidgets.QMessageBox.information(
                self, "Feature Selected", f"Selected Feature ID: {feature.id()}\n" f"Attributes: {feature.attributes()}"
            )

    def closeEvent(self, event):
        self.closingPlugin.emit()
        event.accept()
