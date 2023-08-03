from PyQt6 import QtCore, QtGui, QtWidgets
from lib.ui.WidgetFactory.CodeEditors.SQLEditor import sql_editor


class ScriptEditorDialog(QtWidgets.QDialog):

    def __init__(self, application, script_content):
        super(ScriptEditorDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application

        self.setWindowTitle(self.application.windowTitle() + " - SQL Editor") 
        self.setMinimumSize(500, 500)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        
        self.editor = sql_editor(self.application)
        self.editor.setText(script_content)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.layout.addWidget(self.editor, 0, 0, 1, 2)
        self.layout.addWidget(self.buttonBox, 1, 1, 2, 1)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        QtCore.QMetaObject.connectSlotsByName(self)

    @property 
    def script(self):
        return self.editor.text()
        