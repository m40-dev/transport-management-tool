from PyQt6 import QtCore, QtWidgets
from ..DialogScreens.CustomDialogWindow import CustomDialogWindow
from datetime import datetime

class DatabaseObjectViewer(CustomDialogWindow):

    def __init__(self, application):
        super(DatabaseObjectViewer, self).__init__(application=application, dialog_name="Database Object Viewer")

        # self.form_layout.addWidget(self.preset_name_label, 1, 0, 1, 1)
        self.setupUi()
        
        self.show()

    def setupUi(self):

        self.buttonBox.hide()
        self.setModal(False)
        self.tableWidget = QtWidgets.QTableWidget(2, 2)
        self.tableWidget.setObjectName("DatabaseObjectViewer")
        self.tableWidget.setColumnWidth(0, round(self.width()* 0.45))
        self.tableWidget.setColumnWidth(1, round(self.width()* 0.45))
        # self.tableWidget.horizontalHeader().setVisible(False)

        self.form_layout.addWidget(self.tableWidget, 0, 0 )
        self.restoreWindowState()

    def setTableHeaders(self, headers):
        self.tableWidget.setHorizontalHeaderLabels(headers)

    def loadTableColumn(self, column_index, list_data):
        if len(list_data) > self.tableWidget.rowCount():
            self.tableWidget.setRowCount(len(list_data))
        self.tableWidget.resizeRowsToContents()

        i=0
        for element in list_data:
            cell_item = QtWidgets.QLabel()
            cell_item.setProperty("TableWidget", f"Col_{column_index}")
            display_text = element
            if isinstance(element, datetime):
                display_text = f'{element:%Y-%m-%d %H:%M:%S%z}'

            cell_item.setText(str(display_text))
            cell_item.setWordWrap(True)
            cell_item.setTextInteractionFlags(QtCore.Qt.TextInteractionFlag.TextSelectableByMouse | QtCore.Qt.TextInteractionFlag.TextSelectableByKeyboard)

            self.tableWidget.setCellWidget(
                i, 
                column_index, 
                cell_item)
            i += 1

    def restoreWindowState(self):
        """ Restore window settings """
        # print("restore window")
        self.settings = self.application.settings
        if self.settings.value("DatabaseObjectViewerWindow") is not None:
            self.restoreGeometry(self.settings.value("DatabaseObjectViewerWindow"))

    def saveWindowState(self):
        # print("save window")
        self.application.settings.setValue("DatabaseObjectViewerWindow", self.saveGeometry())

    def close(self, accepted=False):
        self.saveWindowState()
        super().close(accepted=accepted)