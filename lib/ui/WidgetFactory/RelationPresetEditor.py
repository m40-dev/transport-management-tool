# Standard modules


#""" Required QT Libraries """
from PyQt6 import QtWidgets, QtCore


# Data Models
# from lib.data.DataModels import RelationPresetConfigurationModel

class RelationPresetEditor(QtWidgets.QWidget):

    def __init__(self, parent, preset_data):
        super().__init__(parent=parent, flags=QtCore.Qt.WindowType.Dialog)
        self.parent = parent
        self.application = parent
        self.preset_data = preset_data

        self.setupUi()
        self.show()

    def setupUi(self):
        self.layout = QtWidgets.QGridLayout(self)
        self.RelationPresetTreeView = QtWidgets.QTreeView()

        self.layout.addWidget(self.RelationPresetTreeView, 0, 0, 1, 1)