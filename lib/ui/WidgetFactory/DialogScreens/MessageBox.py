from PyQt6 import QtCore, QtGui, QtWidgets

class MsgBox(QtWidgets.QDialog):

    EXCEPTION = "Exception"
    QUESTION = "Question"
    Information = "Question"

    def __init__(self, application=None, message=None, detailed_message=None, window_mode=EXCEPTION):
        super(MsgBox, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application

        self.setWindowTitle(f"{self.application.application_name} - {window_mode}") 
        # self.setMinimumSize(400, 250)
        self.setModal(True)

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setObjectName("layout")

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        
        if detailed_message is not None:
            self.textinput = QtWidgets.QTextEdit(self)
            self.textinput.setVisible(False)
            self.textinput.setAcceptRichText(True)
            self.textinput.document().setDefaultStyleSheet(self.application.color_theme.style_sheet)

            self.textinput.setHtml(f'<pre class="MessageBox-DetailedMessage">{detailed_message}</pre>')

            self.details_button = QtWidgets.QPushButton(self)
            self.details_button.setText("Show Details")
            self.details_button.clicked.connect(self.toggle_details)

            self.layout.addWidget(self.textinput, 1, 0, 1, 3)
            self.layout.addWidget(self.details_button, 2, 0, 1, 1)

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)

        if window_mode == self.QUESTION:
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Yes | 
                QtWidgets.QDialogButtonBox.StandardButton.No)
        else:
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
        
        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.label, 0, 0, 1, 3)
        
        self.layout.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.layout.setRowStretch(1, 2)
        self.label.setText(message)
        self.restoreWindowState()
        self.accepted = bool(self.exec())

    def restoreWindowState(self):
        """ Restore window settings """
        # print("restore window")
        self.settings = self.application.settings
        if self.settings.value("MessageBoxGeometry") is not None:
            self.restoreGeometry(self.settings.value("MessageBoxGeometry"))
        # if self.settings.value("EditorDialogState") is not None:
        #     self.restoreState(self.settings.value("EditorDialogState"))

    def saveWindowState(self):
        # print("save window")
        self.application.settings.setValue("MessageBoxGeometry", self.saveGeometry())
        # self.application.settings.setValue("EditorDialogState", self.saveState())
    
    def toggle_details(self, state):
        # print(state)
        self.textinput.setVisible(not self.textinput.isVisible())
        # self.adjustSize()

    def accept(self):
        self.saveWindowState()
        super().accept()