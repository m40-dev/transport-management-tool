from PyQt6 import QtCore, QtWidgets, QtGui

from pathlib import Path
import json
import uuid
from .MessageBox import MsgBox
import re

class FormEditorDialog(QtWidgets.QDialog):

    def __init__(self, application, configuration_class, dialog_name="Data Editor", form_configuration=None):
        super(FormEditorDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.configuration_class = configuration_class
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self._form_confguration = self.application.getConfigurationParameters(configuration_class)
        if form_configuration is not None:
            self._form_confguration = form_configuration
        self._form_data = {}
        self._base_object = None
        self._base_object_data = None
        self.setMinimumSize(400, 400)
        self.useExperimentalFeatures = self.ProgramConfiguration.getConfigurationValue("ObjectModel", "UseExperimental")
        self.columnMappings = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(configuration_class, "ValuePattern")
            
        self.setWindowTitle(f"{self.application.application_name} - {dialog_name}") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        self.layout.setSpacing(2)
        # self.templatesApplied = True
        
        self.editors = {}
        self.setup_form()
        self.templatesApplied = True

        self.buttonBox = QtWidgets.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.StandardButton.Cancel|QtWidgets.QDialogButtonBox.StandardButton.Ok)
        self.buttonBox.setObjectName("buttonBox")

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout.setRowStretch(self.layout.rowCount(), 2)
        self.layout.setColumnStretch(self.layout.columnCount()-1, 2)
        self.layout.addWidget(self.buttonBox, self.layout.rowCount()+1, 1, 1, 2)
        self.restoreWindowState()

    def restoreWindowState(self):
        """ Restore window settings """
        # print("restore window")
        self.settings = self.application.settings
        if self.settings.value("EditorDialogGeometry") is not None:
            self.restoreGeometry(self.settings.value("EditorDialogGeometry"))

    def saveWindowState(self):
        # print("save window")
        self.application.settings.setValue("EditorDialogGeometry", self.saveGeometry())

    def accept(self):
        self.saveWindowState()
        # if self.useExperimentalFeatures and len(self.columnMappings) > 0 and not self.templatesApplied:
        #     question = QtWidgets.QMessageBox.question(self, "Reapply Templates?", "There are predefined column mapping patterns in this form.\nWould you like to reapply?")
        #     if question == QtWidgets.QMessageBox.StandardButton.Yes:
        #         self.updateFormPatternsComplete()
        #         return False
        validation_errors = {}
        # self.check_mandatory_columns(validation_errors)
        validation_summary = self.check_validators()
        
        # print("vaildate and accept")
        if len(validation_summary) > 0:
            string_data = json.dumps(validation_summary, indent=4, separators=(',',':'))
            MsgBox(self.application, "Form validation returned errors", string_data)
            return False
        # print("form data", self.form_data)
        super().accept()

    def check_validators(self):
        validation_summary = {}
        for editor_object in self.editors.values():
            if editor_object.editor:
                form_value = self.form_data.get(editor_object.column_name, "")
                validation_result, validation_errors = editor_object.validate(form_value)
                if not validation_result:
                    validation_summary[editor_object.display_name] = validation_errors
        return validation_summary

    def check_mandatory_columns(self, validation_errors={}, error_message = "Mandatory column not set."):
        mandatory_columns = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(self.configuration_class, "IsMandatory")
        if len(mandatory_columns) > 0:
            for column, column_configuration in mandatory_columns.items():
                if column_configuration.get("ShowInEditor", True) == False:
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
            # widget_required = (column_configuration.get("ShowInEditor", True) == True
            row_id = self.layout.rowCount()
            editor_object = FormEditorObject(self, self.application, column, column_configuration)

            if editor_object.default_value:
                self.update_form_data(column, editor_object.default_value)

            if not editor_object.isVisible:
                editor_object.deleteLater()
                continue

            editor_object.dataChanged.connect(self.update_form_data)
            
            if self.useExperimentalFeatures and len(self.columnMappings) > 0:
                editor_object.dataChanged.connect(self.updateFormPatterns)

            if editor_object.editor:
                self.editors[column] = editor_object
                self.layout.addWidget(editor_object.label, row_id, 0)
                if editor_object.isMandatory:
                    self.layout.addWidget(editor_object.MandatoryLabel, row_id, 1)
                self.layout.addWidget(editor_object.editor, row_id, 2)

                # editor_object.set_editor_data(default_value)
        if self.useExperimentalFeatures and len(self.columnMappings) > 0:
            self.useMappings = QtWidgets.QCheckBox("Use Value Templates")
            # self.useMappings.setChecked(True)
            self.useMappings.setProperty("EditorDialog", "PropertyHasValueTemplate")
            self.layout.addWidget(
                self.useMappings, 
                self.layout.rowCount(), 0)
        self.layout.setRowStretch(self.layout.rowCount(), 2)
            

    def updateFormPatterns(self, source_column, source_editor):
        if not self.useMappings.isChecked():
            return False

        for column, column_configuration in self.columnMappings.items():
            if column == source_column:
                #do not recalculate pattern when editing value
                continue
            column_value = self.parseStringPattern(column_configuration.get("ValuePattern", ""))
            editor = self.editors.get(column, None)

            if editor and column_value != editor.getValue():
                editor.set_editor_data(column_value)
            self.update_form_data(column, column_value)
    
    def updateFormPatternsComplete(self):
        for column, column_configuration in self.columnMappings.items():

            column_value = self.parseStringPattern(column_configuration.get("ValuePattern", ""))
            editor = self.editors.get(column, None)

            if editor and column_value != editor.getValue():
                editor.set_editor_data(column_value)

            self.update_form_data(column, column_value)
        self.templatesApplied = True
       
    def parseStringPattern(self, string_pattern):
        regex_pattern = r'%([^%]+)%'
        matches = re.findall(regex_pattern, string_pattern)
        replacement_dict = {}
        
        for column_pattern in matches:
            column_name = column_pattern
            substring_chars = 0
            if ":" in column_pattern:
                #try to substring the value
                column_name, substring_chars = column_pattern.split(":")
                if substring_chars.isnumeric():
                    substring_chars = int(substring_chars)
            
            if column_pattern not in replacement_dict.keys():
                column_value = self.getSourceValue(column_name)
                replacement_dict[column_pattern] = column_value
            
            if substring_chars > 0 and column_pattern in replacement_dict.keys() :
                replacement_dict[column_pattern] = replacement_dict[column_pattern][:substring_chars]
            
        # replacement_dict = self.get_replacement_values(matches, previous_state)
        parsed_string = re.sub(regex_pattern, lambda match: replacement_dict.get(match.group(1), match.group(0)), string_pattern)
        return parsed_string

    def getSourceValue(self, source_mapping):
        if "." in source_mapping:
            source = source_mapping.split(".")[0]
            source_column = source_mapping.split(".")[1:]
            if len(source_column) > 0:
                # more than one level higher, pass this to the source
                source_column = ".".join(source_column)
            if source.upper() == "PARENT" and self._base_object and self._base_object.parent():
                return self._base_object.parent().getSourceValue(source_column)
            
            return self.form_data.get(source_column, "")
        return self.form_data.get(source_mapping, "")

    def update_form_data(self, column, value):
        if column:
            column_configuration = self._form_confguration.get(column, None)
            if column_configuration:
                if column_configuration.get("FieldType", None) == "BooleanInput":
                    value = (str(value) == "2" or str(value) == "True") 
            self._form_data[column] = value
        self.templatesApplied = False

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
                editor_widget.set_editor_data(value)
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
        if not source_item:
            return False
        self._base_object = source_item
        self._base_object_data = source_item.edit_data
        for column, value in source_item.edit_data.items():
            # self.form_data[column]=value
            editor_widget = self.editors.get(column, None)
            if editor_widget:
                #configure the widget with base object value
                editor_widget.set_editor_data(value)
            form_column = self.form_data.get(column, None)
            if form_column and len(str(value).strip()) > 0:
                self.update_form_data(column, value)

class FormEditorObject(QtCore.QObject):
    dataChanged = QtCore.pyqtSignal(str, object)

    def __init__(self, parent, application, column_name, column_configuration):
        super(FormEditorObject, self).__init__()
        self.parent = parent
        self.application = application
        self.column_name = column_name
        self.column_configuration = column_configuration
        self.display_name = column_name
        self._current_value = ""

        display = column_configuration.get("Display", column_name)
        if len(display.strip()) > 0:
            self.display_name = display
        self.useExperimentalFeatures = self.application.ProgramConfiguration.getConfigurationValue("ObjectModel", "UseExperimental")
        self.isMandatory = str(column_configuration.get("IsMandatory", "False")).upper() == "TRUE"
        self.isVisible = str(column_configuration.get("ShowInEditor", "True")).upper() == "TRUE"
        self.label = None
        self.MandatoryLabel = None
        self.editor = None

        self.default_value = column_configuration.get("DefaultValue", "")
        self.widgets = []
        self._opacity = 1 
            
        # setup fields based on their role
        field_role =  column_configuration.get("FieldRole", None)
        if field_role and field_role == "UniqueIdentifier":
            self.default_value = str(uuid.uuid4())

        if self.isVisible:
            self.setupUi()
            # self.setVisible(True)

    def validate(self, check_value):
        validation_status = True
        validation_errors = {}
        if len(str(check_value).strip()) == 0 and self.isMandatory:
            validation_errors.update({"Check Mandatory fields": "Mandatory column not set."})
            validation_status = False

        field_type = self.column_configuration.get("FieldType", None)
        if field_type == "IntegerInput":
            if isinstance(check_value, str) and check_value.isnumeric():
                check_value = int(check_value)
            min_value = self.column_configuration.get("MinValue", None)
            max_value = self.column_configuration.get("MaxValue", None)
            if min_value:
                if check_value < min_value:
                    validation_errors.update({"Check value range": "Form Value below minimum allowed value range."})
                    validation_status = False
            if max_value:
                if check_value > max_value:
                    validation_errors.update({"Check value range": "Form Value above maximum allowed value range."})
                    validation_status = False

        return validation_status, validation_errors

    def setVisible(self, visible):
        for widget in self.widgets:
            if widget:
                widget.setVisible(visible)
                
    def setEnabled(self, enabled):
        for widget in self.widgets:
            if widget:
                widget.setEnabled(enabled)

    def getValue(self):
        return self._current_value

    def setupUi(self):
        widgets = []
        if self.isMandatory:
            self.MandatoryLabel = QtWidgets.QLabel("*")
            self.MandatoryLabel.setProperty("PropertyEditor","IsMandatory")
            widgets.append(self.MandatoryLabel)

        self.label = QtWidgets.QLabel(self.parent)
        self.label.setText(f"<b>{str(self.display_name)}</b>")
        self.editor = self.get_editor()

        tooltip = self.column_configuration.get("Description", "")
        if len(tooltip.strip()) > 0: 
            if self.label:
                self.label.setToolTip(f"<i>{tooltip}</i>")
            if self.editor:
                self.editor.setToolTip(f"<i>{tooltip}</i>")

        widgets.append(self.label)
        widgets.append(self.editor)

        self.set_editor_data(self.default_value)
        self.update_form_data(self.column_name, self.default_value)

        self.widgets = widgets

        if self.useExperimentalFeatures and len(self.column_configuration.get("ValuePattern", "")) > 0:
            self.label.setProperty("EditorDialog", "PropertyHasValueTemplate")

    def update_form_data(self, column, value):
        if self.column_configuration.get("FieldType", None) == "BooleanInput":
            value = (str(value) == "2" or str(value) == "True")
        
        if self.column_configuration.get("FieldType", None) == "IntegerInput":
            if len(str(value).strip()) == 0:
                value = 0
            if str(value).isnumeric():
                value = int(value)
        self._current_value = value
        self.dataChanged.emit(self.column_name, value)

    def set_editor_data(self, value):
        self._current_value = value
        editor_widget = self.editor
        if isinstance(editor_widget, (QtWidgets.QLineEdit, QtWidgets.QTextEdit)):
            editor_widget.setText(str(value))
            # editor_widget.adjustSize()

        if isinstance(editor_widget, QtWidgets.QComboBox):
            index = editor_widget.findData(value, QtCore.Qt.ItemDataRole.UserRole)
            editor_widget.setCurrentIndex(index)

        if isinstance(editor_widget, FileInputWidget):
            editor_widget.setCurrentPath(value)
        
        if isinstance(editor_widget, ListInputWidget):
            editor_widget.setValues(value)
        
        if isinstance(editor_widget, QtWidgets.QCheckBox):
            state = str(value) == "2" or str(value).upper() == "TRUE"
            editor_widget.setChecked(state)

    def get_editor(self):
        column = self.column_name
        column_configuration = self.column_configuration

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
        range_validator = QtGui.QIntValidator(self)
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
        options = column_configuration.get("Options", {"":""})
        editor = QtWidgets.QComboBox()
        editor.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        editor.wheelEvent = lambda event, editor=editor: self.wheelEventHandler(event, editor)
        if isinstance(options, str):
            options = json.loads(options)
            
        for key, value in options.items():
            editor.addItem(key, value)

        editor.currentIndexChanged.connect(
                lambda index, column=column: 
                self.update_form_data(column, editor.itemData(index))
                )

        editor.setProperty("Widget", "EditorDialog")
        return editor

    def wheelEventHandler(self, event, editor=None):
        if editor.hasFocus():
            editor.__class__.wheelEvent(editor, event)
        event.accept()

    def string_input(self, column, column_configuration):
        placeholder_text = column_configuration.get("PlaceholderText", "")

        editor = QtWidgets.QLineEdit()
        editor.setPlaceholderText(placeholder_text)
        
        editor.textChanged.connect(
                lambda value, column=column: 
                self.update_form_data(column, value)
                )
        
        is_sensitive = column_configuration.get("IsSensitive", False) == True
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
        is_sensitive = column_configuration.get("IsSensitive", False) == True
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
        is_sensitive = column_configuration.get("IsSensitive", False) == True
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