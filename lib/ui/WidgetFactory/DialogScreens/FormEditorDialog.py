from PyQt6 import QtCore, QtWidgets, QtGui
from pathlib import Path
import json
import uuid
from .MessageBox import MsgBox

class FormEditorDialog(QtWidgets.QDialog):

    def __init__(self, application, configuration_class, dialog_name="Data Editor"):
        super(FormEditorDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.configuration_class = configuration_class
        self.object_configuration = self.application.object_configuration
        self._form_confguration = self.object_configuration.get(configuration_class)
        self._form_data = {}
        self._base_object_data = None
        self.setMinimumSize(400, 400)

        self.setWindowTitle(f"{self.application.windowTitle()} - {dialog_name}") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        self.layout.setSpacing(2)
        # self.layout.setContentsMargins(QtCore.QMargins(2,2,2,2))
        
        self.editors = {}
        self.setup_form()

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.setRowStretch(self.layout.rowCount(), 2)
        self.layout.addWidget(self.buttonBox, self.layout.rowCount()+1, 1, 1, 2)
        self.restoreWindowState()

    def restoreWindowState(self):
        """ Restore window settings """
        # print("restore window")
        self.settings = self.application.settings
        if self.settings.value("EditorDialogGeometry") is not None:
            self.restoreGeometry(self.settings.value("EditorDialogGeometry"))
        # if self.settings.value("EditorDialogState") is not None:
        #     self.restoreState(self.settings.value("EditorDialogState"))

    def saveWindowState(self):
        # print("save window")
        self.application.settings.setValue("EditorDialogGeometry", self.saveGeometry())
        # self.application.settings.setValue("EditorDialogState", self.saveState())

    def accept(self):
        self.saveWindowState()
        validation_errors = {}
        self.check_mandatory_columns(validation_errors)
        # self.check_mandatory_columns(validation_errors, "Some Additional Error")
        
        print("vaildate and accept")
        if len(validation_errors) > 0:
            string_data = json.dumps(validation_errors, indent=4, separators=(',',':'))
            MsgBox(self.application, "Form validation returned errors", string_data)
            return False
        # print("form data", self.form_data)
        super().accept()

    def check_mandatory_columns(self, validation_errors={}, error_message = "Mandatory column not set."):
        mandatory_columns = self.object_configuration.get_columns_configuration_by_setting(self.configuration_class, "IsMandatory")
        if len(mandatory_columns) > 0:
            for column, column_configuration in mandatory_columns.items():
                if column_configuration.get("ShowInEditor", "True") == "False":
                    # column not visible to user
                    # print(column, "column not visible to user")
                    continue
                    
                if column not in self.editors.keys():
                    # column does not have the editor support
                    # print(column, "column does not have the editor support")
                    continue

                if len(str(self.form_data.get(column, "")).strip()) == 0:
                    if column not in validation_errors.keys():
                        validation_errors[column] = [error_message]
                    else:
                        validation_errors[column].append(error_message) 
        return validation_errors

    def setup_form(self):
        # print("setup form")
        # print(self._form_data)
        for column, column_configuration in self._form_confguration.items():
            widget_required = (column_configuration.get("ShowInEditor", "True") == "True")
            row_id = self.layout.rowCount()
            display_name = column_configuration.get("Display", column)
            default_value = column_configuration.get("DefaultValue", "")
            
            # setup fields based on their role
            field_role =  column_configuration.get("FieldRole", None)
            if field_role and field_role == "UniqueIdentifier":
                default_value = str(uuid.uuid4())

            #set default value only if available. This ensures that only required fields will be updated with the form data
            # having too many columns that are not editable might result in data overwrites where this is not desired (e.g. children data)
            if default_value:
                self.update_form_data(column, default_value)

            if not widget_required:
                continue
            
            is_mandatory = column_configuration.get("IsMandatory", "False") == "True"
            label = QtWidgets.QLabel(str(display_name))
            if is_mandatory:
                mandatory_flag = QtWidgets.QLabel("*")
                mandatory_flag.setProperty("PropertyEditor","IsMandatory")
                self.layout.addWidget(mandatory_flag, row_id, 1)

            editor = self.get_editor(column, column_configuration)
            if editor:
                self.editors[column] = editor
                self.layout.addWidget(label, row_id, 0)
                self.layout.addWidget(editor, row_id, 2)
                self.set_editor_data(editor, default_value)

    def update_form_data(self, column, value):
        if column:
            column_configuration = self._form_confguration.get(column, None)
            if column_configuration:
                if column_configuration.get("FieldType", None) == "BooleanInput":
                    value = (str(value) == "2" or str(value) == "True") 
            self._form_data[column] = value

    @property
    def form_data(self):
        # print("return form data", self._form_data)
        return self._form_data

    def set_dictionary_data(self, dict_data):
        if not dict_data:
            return False
        for column, value in dict_data.items():
            editor_widget = self.editors.get(column, None)
            if editor_widget:
                #configure the widget with base object value
                self.set_editor_data(editor_widget, value)
            form_column = self.form_data.get(column, None)
            if form_column and len(str(value).strip()) > 0:
                self.update_form_data(column, value)

    def set_form_data(self, source_index):
        #configures the editors based on the source data of the object
        #sets the values for any hidden items as well
        source_item = None
        if source_index.isValid():
            source_item = source_index.internalPointer()
        else:
            return False
        self._base_object_data = source_item.edit_data
        for column, value in source_item.edit_data.items():
            # self.form_data[column]=value
            editor_widget = self.editors.get(column, None)
            if editor_widget:
                #configure the widget with base object value
                self.set_editor_data(editor_widget, value)
            form_column = self.form_data.get(column, None)
            if form_column and len(str(value).strip()) > 0:
                self.update_form_data(column, value)

    def set_editor_data(self, editor_widget, value):
        if isinstance(editor_widget, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
            editor_widget.setText(str(value))
            editor_widget.adjustSize()

        if isinstance(editor_widget, QtWidgets.QComboBox):
            index = editor_widget.findData(value, QtCore.Qt.ItemDataRole.UserRole)
            editor_widget.setCurrentIndex(index)

        if isinstance(editor_widget, FileInputWidget):
            editor_widget.setCurrentPath(value)
        
        if isinstance(editor_widget, ListInputWidget):
            editor_widget.setValues(value)
        
        if isinstance(editor_widget, QtWidgets.QCheckBox):
            state = str(value) == "2" or str(value) == "True"
            editor_widget.setChecked(state)

    def get_editor(self, column, column_configuration):
        supported_types = ["StringInput", "TextInput", "FixedInput", "FileInput", "ListInput", "IntegerInput", "BooleanInput"]

        field_type = column_configuration.get("FieldType", None)
        
        if field_type is None or field_type not in supported_types:
            return None

        if field_type == "StringInput":
            return self.string_input(column, column_configuration)

        if field_type == "TextInput":
            return self.text_input(column, column_configuration)

        if field_type == "FixedInput":
            return self.fixed_input(column, column_configuration)
        
        if field_type == "FileInput":
            return self.file_input(column, column_configuration)

        if field_type == "ListInput":
            return self.list_input(column, column_configuration)
        
        if field_type == "IntegerInput":
            editor = self.integer_input(column, column_configuration)
            return editor
        
        if field_type == "BooleanInput":
            editor = self.boolean_input(column, column_configuration)
            return editor
        
        return None

    def boolean_input(self, column, column_configuration):
        editor = QtWidgets.QCheckBox()
        editor.stateChanged.connect(
                lambda value, column=column: 
                self.update_form_data(column, value)
                )
        editor.setProperty("Widget", "EditorDialog")
        return editor

    def integer_input(self, column, column_configuration):
        editor = self.string_input(column, column_configuration)
        min_value = column_configuration.get("MinValue", 1)
        max_value = column_configuration.get("MaxValue", 255)
        range_validator = QtGui.QIntValidator(min_value, max_value, self)
        editor.setValidator(range_validator)
        return editor

    def list_input(self, column, column_configuration):
        editor = ListInputWidget(
            application=self.application, 
            column_name=column, 
            column_configuration=column_configuration
            )
        editor.list_changed.connect(
            lambda value, column=column: 
            self.update_form_data(column, value)
            )
        return editor

    def fixed_input(self, column, column_configuration):
        options = column_configuration.get("Options", {})
        editor = QtWidgets.QComboBox()
        
        for key, value in options.items():
            editor.addItem(key, value)

        editor.currentIndexChanged.connect(
                lambda index, column=column: 
                self.update_form_data(column, editor.itemData(index))
                )

        editor.setProperty("Widget", "EditorDialog")
        return editor

    def string_input(self, column, column_configuration):
        placeholder_text = column_configuration.get("PlaceholderText", "")

        editor = QtWidgets.QLineEdit()
        editor.setPlaceholderText(placeholder_text)
        
        editor.textChanged.connect(
                lambda value, column=column: 
                self.update_form_data(column, value)
                )
        
        is_sensitive = column_configuration.get("IsSensitive", "False") == "True"
        if is_sensitive:
            editor.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        editor.setProperty("Widget", "EditorDialog")
        return editor

    def text_input(self, column, column_configuration):
        placeholder_text = column_configuration.get("PlaceholderText", "")

        editor = QtWidgets.QTextEdit()
        editor.setPlaceholderText(placeholder_text)

        editor.textChanged.connect(
                lambda column=column: 
                self.update_form_data(column, editor.toPlainText())
                )
        
        editor.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        is_sensitive = column_configuration.get("IsSensitive", "False") == "True"
        if is_sensitive:
            editor.setEchoMode(QtWidgets.QTextEdit.EchoMode.Password)
        editor.setProperty("Widget", "EditorDialog")
        
        return editor

    def file_input(self, column, column_configuration):
        editor = FileInputWidget(
            application=self.application, 
            column_name=column, 
            column_configuration=column_configuration
            )
        editor.file_path_changed.connect(
            lambda value, column=column: 
            self.update_form_data(column, value)
            )
        
        return editor

class FormEditorWidget(QtWidgets.QWidget):
    def __init__(self, application, column_name, column_configuration):
        super(FormEditorWidget, self).__init__(
            flags=QtCore.Qt.WindowType.Dialog, 
            parent=application)
        
        self.application = application
        self.column_confguration = column_configuration
        self.placeholder_text = column_configuration.get("PlaceholderText", "")

        self.layout = QtWidgets.QHBoxLayout(self)
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(QtCore.QMargins(0,0,0,0))
        self.setProperty("Widget", "EditorDialog")

class ListInputWidget(FormEditorWidget):
    list_changed = QtCore.pyqtSignal(list)

    def __init__(self, application, column_name, column_configuration):
        super(ListInputWidget, self).__init__(
            application=application, 
            column_name=column_name, 
            column_configuration=column_configuration)

        self.list_input=QtWidgets.QTextEdit()
        self.list_input.setPlaceholderText(self.placeholder_text)
        is_sensitive = column_configuration.get("IsSensitive", "False") == "True"
        if is_sensitive:
            self.list_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.list_input.textChanged.connect(self.updateValues)
        self.layout.addWidget(self.list_input)

        self.list_input.setProperty("Widget", "EditorDialog")
        self.list_input.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)

    def setValues(self, value_list):
        if value_list is None:
            return False
        separator = self.column_confguration.get("Separator", ",")
        separator += " "
        self.list_input.setText(separator.join(value_list))

    def getValues(self):
        separator = self.column_confguration.get("Separator", ",")
        editor_text = self.list_input.toPlainText()
        values = editor_text.split(separator)
        return map(str.strip, values)

    def updateValues(self):
        self.list_changed.emit(self.getValues())


class FileInputWidget(FormEditorWidget):
    file_path_changed = QtCore.pyqtSignal(str)

    def __init__(self, application, column_name, column_configuration):
        super(FileInputWidget, self).__init__(
            application=application, 
            column_name=column_name, 
            column_configuration=column_configuration)

        self.path_button = QtWidgets.QToolButton()
        self.path_button.setText("...")

        self.path_input=QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText(self.placeholder_text)
        is_sensitive = column_configuration.get("IsSensitive", "False") == "True"
        if is_sensitive:
            self.path_input.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.layout.addWidget(self.path_input)
        self.layout.addWidget(self.path_button)

        self.path_input.setProperty("Widget", "EditorDialog")
        self.path_button.setProperty("Widget", "EditorDialog")
        self.path_input.textChanged.connect(self.file_path_changed)
        self.path_button.clicked.connect(
            lambda column=column_name, column_configuration=column_configuration: 
            self.get_file_path(column, column_configuration)
            )

    def get_file_path(self, column, column_configuration):
        file_filter = column_configuration.get("FileExtension", "*")
        path_mode = column_configuration.get("FileSelectionMode", "Absolute")
        dialog = QtWidgets.QFileDialog(self, "Transport Manager - Get File Path", 
            self.application.current_workdir)

        dialog = QtWidgets.QFileDialog(self, "Transport Manager - Get Path", 
        self.application.current_workdir)

        if path_mode == "DirectoryPath":
            file_path = [dialog.getExistingDirectory()]
        else:
            file_path = dialog.getSaveFileName(filter=file_filter)

        if file_path[0] != "":
            file_path = file_path[0]
            if path_mode == "Relative" and self.application.current_workdir is not None:
                file_path = Path(file_path).relative_to(self.application.current_workdir)
            if path_mode == "FileName":
                file_path = Path(file_path).name
            self.setCurrentPath(str(file_path))

    def setCurrentPath(self, new_path):
        self.path_input.setText(new_path)
        self.file_path_changed.emit(new_path)

    def currentPath(self):
        return self.file_input.text()