from PyQt6 import QtCore, QtGui, QtWidgets
from lib.ui.WidgetFactory.DialogScreens.CustomDialogWindow import CustomDialogWindow
from lib.ui.WidgetFactory.DialogScreens.MessageBox import MsgBox


class EncryptionKeyDialog(CustomDialogWindow):

    def __init__(self, application, initial=False):
        # super(EncryptionKeyDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)
        super(EncryptionKeyDialog, self).__init__(application=application, restore_window_state=False)

        self.application = application
        self.setMinimumSize(250, 150)
        
        description_text = "Please provide the main password to decrypt session details:"
        
        if initial:
            description_text = "Please set the main password that will be used to encrypt the session details:"

        self.description = QtWidgets.QLabel(description_text)
        self.key_label = QtWidgets.QLabel("Encryption Key:")
        self.key_input = QtWidgets.QLineEdit(self)
        self.key_input.setFocus(QtCore.Qt.FocusReason.ActiveWindowFocusReason)
        self.key_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        
        self.key_confirm = None
        
        if initial:
            self.key_confirm_label = QtWidgets.QLabel("Confirm Key:")
            self.key_confirm = QtWidgets.QLineEdit()
            self.key_confirm.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        if not initial:
            self.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)

        self.form_layout.addWidget(self.description, 0, 0, 1, 0)
        self.form_layout.addWidget(self.key_label, 1, 0, 1, 1)
        self.form_layout.addWidget(self.key_input, 1, 1, 1, 1)

        if initial:
            self.form_layout.addWidget(self.key_confirm_label, 2, 0, 1, 1)
            self.form_layout.addWidget(self.key_confirm, 2, 1, 1, 1)
        self.form_layout.setRowStretch(3, 1)

    @property 
    def encryption_key(self):
        return self.key_input.text()
        
    def accept(self):
        if self.key_confirm and self.key_input.text() != self.key_confirm.text():
            dialog = MsgBox(
                application=self.application, 
                window_title="Key does not match",
                message="Provided key does not match the confirmation.", 
                window_mode=MsgBox.INFO)
            # QtWidgets.QMessageBox.information(self.application, "Key does not match", "Provided key does not match the confirmation.")
            return False
        super().accept()

    