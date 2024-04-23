from PyQt6 import QtCore, QtGui, QtWidgets
from .CustomDialogWindow import CustomDialogWindow
from platform import python_version

class MsgBox(CustomDialogWindow):

    EXCEPTION = "Exception"
    QUESTION = "Question"
    INFO = "Information"

    def __init__(self, application, window_title="", message=None, detailed_message=None, window_mode=EXCEPTION):
        super(MsgBox, self).__init__(application=application, dialog_name=window_title, restore_window_state=False)
        self.message = message
        self.detailed_message = detailed_message
        self.window_mode = window_mode
        self.setupUi()
        self.exec()
    
    def setupUi(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setTextFormat(QtCore.Qt.TextFormat.RichText)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        
        if self.detailed_message is not None:
            self.textinput = QtWidgets.QTextEdit(self)
            self.textinput.setProperty("MessageBox", "DetailedMessage")

            self.textinput.setVisible(False)
            self.textinput.setAcceptRichText(True)
            self.textinput.setReadOnly(True)

            self.textinput.document().setDefaultStyleSheet(self.application.color_theme.style_sheet)
            message = ""
            max_line_width = 120
            for line in self.detailed_message.splitlines():
                if len(line) > max_line_width:
                    while len(line) > max_line_width:
                        message += line[:max_line_width] + "\n"
                        line = line[max_line_width:]
                    message += line + "\n"
                else:
                    message += line + "\n"

            self.textinput.setHtml(f'<div class="MessageBox-DetailedMessage"><pre>{message}</pre></div>')
            self.details_button = QtWidgets.QPushButton(self)
            self.details_button.setText("Toggle Details")
            self.details_button.clicked.connect(self.toggle_details)

            self.form_layout.addWidget(self.textinput, 1, 0)
            self.form_layout.addWidget(self.details_button, 2, 0)

        if self.window_mode == self.QUESTION:
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Yes | 
                QtWidgets.QDialogButtonBox.StandardButton.No)
            icon = self.ProgramConfiguration.getIcon("ExecutionLogs")
            self.setIcon(icon)
        else:
            self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Close)
        
        self.form_layout.addWidget(self.label, 0, 0)
        self.label.setText(self.message)

        self.setMinimumSize(200, 150)

    def toggle_details(self, state):
        self.textinput.setVisible(not self.textinput.isVisible())
        if self.textinput.isVisible():
            self.resize(600, 350)
        else:
            self.resize(200, 150)

class AboutWindow(CustomDialogWindow):

    def __init__(self, application):
        super(AboutWindow, self).__init__(
            application=application,
            dialog_name="About Application", 
            restore_window_state=False)
        
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.setupUi()
        self.exec()

    def setupUi(self):
        self.setMinimumSize(300, 350)
        self.resize(600, 800)

        self.description_input = QtWidgets.QTextBrowser(self)
        self.description_input.setReadOnly(True)
        self.description_input.setAcceptRichText(True)
        self.description_input.setTextInteractionFlags(
            QtCore.Qt.TextInteractionFlag.TextBrowserInteraction
            )
        self.description_input.anchorClicked.connect(self.openHyperlink)
        self.description_input.setOpenLinks(False)

        self.form_layout.addWidget(self.description_input, 0, 0)
        self.setDescriptionText()
    
    def openHyperlink(self, hyperlink):
        QtGui.QDesktopServices.openUrl(hyperlink)

    def setDescriptionText(self):
        source_file = self.application.load_file("./Documentation/About")
        pyqt_version = QtCore.PYQT_VERSION_STR
        python_ver = python_version()

        source_file = source_file.replace(b'%APP_VERSION%', bytes(self.application.application_version, 'utf-8'))
        source_file = source_file.replace(b'%PYQT_VERSION%', bytes(pyqt_version, 'utf-8'))
        source_file = source_file.replace(b'%PYTHON_VERSION%', bytes(python_ver, 'utf-8'))
        if source_file:
            self.description_input.setHtml(source_file.decode("utf-8"))
        