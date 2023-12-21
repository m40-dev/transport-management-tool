from PyQt6 import QtCore, QtGui, QtWidgets
from .CustomDialogWindow import CustomDialogWindow

class MsgBox(CustomDialogWindow):

    EXCEPTION = "Exception"
    QUESTION = "Question"
    Information = "Question"

    def __init__(self, application, message=None, detailed_message=None, window_mode=EXCEPTION):
        super(MsgBox, self).__init__(application=application, dialog_name="MessageBox")
        self.message = message
        self.detailed_message = detailed_message
        self.window_mode = window_mode

        self.setModal(True)
        self.setupUi()
    
    def setupUi(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        if self.detailed_message is not None:
            self.textinput = QtWidgets.QTextEdit(self)
            self.textinput.setProperty("MessageBox", "DetailedMessage")

            self.textinput.setVisible(False)
            self.textinput.setAcceptRichText(True)

            self.textinput.document().setDefaultStyleSheet(self.application.color_theme.style_sheet)
            self.textinput.setHtml(f'<pre class="MessageBox-DetailedMessage">{self.detailed_message}</pre>')

            self.details_button = QtWidgets.QPushButton(self)
            self.details_button.setText("Show Details")
            self.details_button.clicked.connect(self.toggle_details)

            self.form_layout.addWidget(self.textinput, 1, 0, 1, 3)
            self.form_layout.addWidget(self.details_button, 2, 0, 1, 1)


        if self.window_mode == self.QUESTION:
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Yes | 
                QtWidgets.QDialogButtonBox.StandardButton.No)
        else:
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
        
        self.buttonBox.setObjectName("buttonBox")
        self.form_layout.addWidget(self.label, 0, 0, 1, 3)
        self.label.setText(self.message)

    def toggle_details(self, state):
        # print(state)
        self.textinput.setVisible(not self.textinput.isVisible())
