from PyQt6 import QtCore, QtWidgets
from pathlib import Path
import json
import uuid

class FormEditorDialog(QtWidgets.QDialog):

    def __init__(self, application, form_confguration={}, dialog_name="Data Editor"):
        super(FormEditorDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self._form_confguration = form_confguration
        self._form_data = {}
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

            #set default value
            self._form_data[column] = default_value

            if not widget_required:
                continue

            label = QtWidgets.QLabel(str(display_name))
            editor = self.get_editor(column, column_configuration)
            if editor:
                self.editors[column] = editor
                self.layout.addWidget(label, row_id, 0)
                self.layout.addWidget(editor, row_id, 1)
                self.set_editor_data(editor, default_value)

    def update_form_data(self, column, value):
        # print("update form data", column, value)
        self._form_data[column] = value

    @property
    def form_data(self):
        print("return form data", self._form_data)
        return self._form_data

    def set_form_data(self, source_index):
        source_item = None
        if source_index.isValid():
            source_item = source_index.internalPointer()
        else:
            return False

        for column, value in source_item.edit_data.items():
            editor_widget = self.editors.get(column, None)
            self.set_editor_data(editor_widget, value)

    def set_editor_data(self, editor_widget, value):
        if isinstance(editor_widget, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
            editor_widget.setText(value)

        if isinstance(editor_widget, QtWidgets.QComboBox):
            editor_widget.setCurrentText(value)

        if isinstance(editor_widget, FileInputWidget):
            editor_widget.setCurrentPath(value)
        
        if isinstance(editor_widget, ListInputWidget):
            editor_widget.setValues(value)


    def get_editor(self, column, column_configuration):
        supported_types = ["StringInput", "TextInput", "FixedInput", "FileInput", "ListInput"]

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
        
        return None

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
        
        editor.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContentsOnFirstShow)
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

        self.layout.addWidget(self.path_input)
        self.layout.addWidget(self.path_button)

        self.path_input.setProperty("Widget", "EditorDialog")
        self.path_button.setProperty("Widget", "EditorDialog")
        self.path_input.textChanged.connect(self.setCurrentPath)
        self.path_button.clicked.connect(
            lambda column=column_name, column_configuration=column_configuration: 
            self.get_file_path(column, column_configuration)
            )

    def get_file_path(self, column, column_configuration):
        file_filter = column_configuration.get("FileExtension", "*")
        path_mode = column_configuration.get("FilePathMode", "Absolute")
        dialog = QtWidgets.QFileDialog(self, "Transport Manager - Get File Path", 
            self.application.current_workdir)

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