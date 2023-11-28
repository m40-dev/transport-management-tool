from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import (
    QMenu, QMessageBox
    )
#""" built-in modules """
import hashlib
import json
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64, os

import lib.ui.WidgetFactory as WidgetFactory
import lib.ui.WidgetFactory.DialogScreens as DialogScreens
from lib.db.database import DatabaseConnection 

class ConnectionHandler(QObject):
    databaseConnectionEstablished = pyqtSignal()

    def __init__(self, application):
        super().__init__(parent=application)
        self.application = application
        self.encryption_key = None
        self.connections = {}
        self.loadSavedConnections()
        
    def loadSavedConnections(self):
        """ Load Saved connection data """
        connections = self.application.settings.value("Connections")
        if connections is None:
            self.connections = {}
            return False

        if len(connections) > 0:
            encryption_key = self.getEncryptionKey()
            if encryption_key:
                self.encryption_key = encryption_key
                if self.decryptConnectionData(connections):
                    self.loadConnectionData()
                else:
                    # print("connection data decryption failed")
                    self.connections = {}
                    decision = QMessageBox.question(self.application, "Connection data decryption failed", "Do you want to try again?\nIf not, the connection sessions will not be available.")
                    if decision == QMessageBox.StandardButton.Yes:
                        self.loadSavedConnections()
            else:
                # print("connection details were not loaded")
                self.connections = {}
                decision = QMessageBox.question(
                    self.application, 
                    "Connection data decryption skipped.", 
                    "There was no encryption key provided to decrypt data,\ndo you want to continue without session configurations?")
                
                if decision == QMessageBox.StandardButton.No:
                    self.loadSavedConnections()

    """ connection Data Management """
    def getEncryptionKey(self, initial=False):
        encryption_key = DialogScreens.EncryptionKeyDialog(self.application, initial)
        if encryption_key.exec():
            if len(encryption_key.encryption_key) > 0:
                enc = hashlib.sha3_512(bytes(encryption_key.encryption_key, 'utf-8'))
                return enc.hexdigest()
        return False
        
    def decryptConnectionData(self, encrypted_connection_details):

        if isinstance(encrypted_connection_details, dict):
            return True

        if self.encryption_key is None:
            self.encryption_key = self.getEncryptionKey()

        if not self.encryption_key:
            return False

        byte_key = bytes(self.encryption_key, 'utf-8')[0:32]
        b64_byte_key = base64.urlsafe_b64encode(byte_key)

        salt = self.application.settings.value("ApplicationId")
        if salt:
            kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    iterations=480000,
                    salt=salt
                )
            byte_key = kdf.derive(bytes(self.encryption_key, 'utf-8'))
            b64_byte_key = base64.urlsafe_b64encode(byte_key)
        else:
            # random ApplicationId was not generated yet
            salt = os.urandom(32)
            self.application.settings.setValue("ApplicationId", salt)
        try:
            crypto = Fernet(b64_byte_key)
            decrypted_connection_details = crypto.decrypt(encrypted_connection_details)
        except:
            return False

        connection_data = json.loads(decrypted_connection_details)
        if connection_data:
            self.connections = connection_data
            return True
        return False

    def saveConnectionsData(self):
        if len(self.connections) == 0:
            self.application.settings.setValue("Connections", {})
            return True
        
        encoded_connection_data = json.dumps(self.connections).encode('utf-8')

        if self.encryption_key is None:
            self.encryption_key = self.getEncryptionKey(initial=True)
        
        if not self.encryption_key:
            #operation cancelled
            return False

        salt = self.application.settings.value("ApplicationId")
        if not salt:
            salt = os.urandom(32)
            self.application.settings.setValue("ApplicationId", salt)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            iterations=480000,
            salt=salt
        )
        
        if self.encryption_key:
            # byte_key = bytes(self.encryption_key, 'utf-8')[0:32]
            byte_key = kdf.derive(bytes(self.encryption_key, 'utf-8'))
            b64_byte_key = base64.urlsafe_b64encode(byte_key)
            crypto = Fernet(b64_byte_key)
            encrypted_connection_details = crypto.encrypt(encoded_connection_data)

            self.application.settings.setValue("Connections", encrypted_connection_details)
            self.application.connectionDataChanged.emit()

    def loadConnectionData(self):
        if self.connections is not None:
            if isinstance(self.connections, dict):
                for connection_name in self.connections.keys():
                    self.addConnectionMenuEntry(connection_name)

    def getConnectionDetails(self, connection_name=None):
        connection_data = self.connections.get(connection_name, None)

        editor_configuration = Connection_Form_Configuration
        if editor_configuration:
            dialog = WidgetFactory.FormEditorDialog(self.application, 
            configuration_class="Connection_Configuration",
            dialog_name="Connection Configuration",
            form_configuration=editor_configuration
            )
            dialog.set_dictionary_data(connection_data)
            if dialog.exec():
                data = dialog.form_data
                dialog_connection_name = data.get("ConnectionName", None)

                if dialog_connection_name and dialog_connection_name not in self.connections.keys() and not connection_name:
                    self.addConnectionMenuEntry(dialog_connection_name)

                if connection_name and dialog_connection_name != connection_name:
                    source_connection = self.application.ui.menuConnections.findChildren(QMenu, connection_name, Qt.FindChildOption.FindDirectChildrenOnly)
                    if len(source_connection) == 1:
                        source_connection = source_connection[0]
                        source_connection.setObjectName(dialog_connection_name)
                        source_connection.setTitle(dialog_connection_name)
                        self.connections.pop(connection_name)

                self.connections[dialog_connection_name] = data
                self.saveConnectionsData()

    def addConnectionMenuEntry(self, connection_name):
        NewMenuItem = self.application.ui.menuConnections.addMenu(connection_name)
        NewMenuItem.setObjectName(connection_name)
        ConnectAction = NewMenuItem.addAction("Connect")
        EditAction = NewMenuItem.addAction("Edit")
        NewMenuItem.addSeparator()
        DeleteAction = NewMenuItem.addAction("Delete")
        ConnectAction.triggered.connect(lambda: self.connectDatabase(NewMenuItem.objectName()))
        EditAction.triggered.connect(lambda: self.getConnectionDetails(NewMenuItem.objectName()))
        DeleteAction.triggered.connect(lambda: self.deleteConnectionEntry(NewMenuItem))

    def deleteConnectionEntry(self, connection_menu_object):
        connection_name = connection_menu_object.title()

        decision = QMessageBox.question(self.application, "Confirm connection Delete", f"Are you sure to delete connection info: {connection_name}?")
        if decision == QMessageBox.StandardButton.Yes:
            action = connection_menu_object.menuAction()
            self.application.ui.menuConnections.removeAction(action)
            
            self.connections.pop(connection_name)
            self.saveConnectionsData()

        """ Database connection Management """
    def connectDatabase(self, connection_name):
        if not isinstance(self.connections, dict):
            return False
        
        if connection_name not in self.connections.keys():
            return False
        
        self.application.ui.statusbar.showMessage(f"Using connection info: {connection_name}")

        connection_params = self.connections[connection_name]

        if self.application.db is not None:
            self.application.db.disconnect_db()

        self.application.db = DatabaseConnection(connection_params)
        self.application.db.connect_db()
        
        if self.application.db and self.application.db.is_connected:
            self.databaseConnectionEstablished.emit()

Connection_Form_Configuration = {
        "ConnectionName": 
            {
                "FieldType": "StringInput",
                "Display": "Connection Name",
                "PlaceholderText": "Provide Connection Name",
                "FieldRole": "DisplayRole",
                "IsMandatory": True
            },
        "Description": 
            {
                "FieldType": "TextInput",
                "Display": "Connection Description",
                "PlaceholderText": "Connection Description",
                "FieldRole": "DescriptionRole"
            },
        "ServerAddress":
            {
                "FieldType": "StringInput",
                "IsMandatory": True,
                "Display": "Server Address"
            },
        "DatabaseName":
            {
                "FieldType": "StringInput",
                "IsMandatory": True,
                "Display": "Database Name"
            },
        "SQLUserName":
            {
                "FieldType": "StringInput",
                "IsMandatory": True,
                "Display": "SQL User Name"
            },
        "SQLPassword":
            {
                "FieldType": "StringInput",
                "IsSensitive": True ,
                "IsMandatory": True,
                "Display": "SQL User Password"
            },
        "ApplicationUserName":
            {
                "FieldType": "StringInput",
                "IsMandatory": True,
                "Display": "Application User Name"
            },
        "ApplicationPassword":
            {
                "FieldType": "StringInput",
                "IsSensitive": True,
                "IsMandatory": True,
                "Display": "Application User Password"
            },
        "EncryptConnection":
            {
                "FieldType": "BooleanInput",
                "DefaultValue": True,
                "Display": "Force Encryption"
            },
        "ToolsDirectory":
            {
                "FieldType": "FileInput",
                "FileSelectionMode": "DirectoryPath",
                "Display": "Identity Manager Tools Location"
            }
        }