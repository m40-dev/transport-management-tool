from PyQt6 import QtCore, QtWidgets, QtGui
from .MessageBox import MsgBox

class MultiObjectEditorForm(QtWidgets.QDialog):

    def __init__(self, application, configuration_class, dialog_name="Data Editor - Column Selection", form_configuration=None):
        super(MultiObjectEditorForm, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)

        self.application = application
        self.configuration_class = configuration_class
        self._form_confguration = self.application.getConfigurationParameters(configuration_class)
        if form_configuration is not None:
            self._form_confguration = form_configuration
        self._form_data = {}
        self._base_object_data = None
        self.setMinimumSize(400, 400)

        self.setWindowTitle(f"{self.application.application_name} - {dialog_name}") 

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("layout")
        self.layout.setSpacing(2)
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
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

    def setup_form(self):
        description_label = QtWidgets.QLabel("Select Columns to be updated in bulk for all selected items.\nOnly same object class items will be updated.")
        self.layout.addWidget(description_label, self.layout.rowCount(), 0, 2, 2)
        for column, column_configuration in self._form_confguration.items():
            widget_required = (column_configuration.get("ShowInEditor", True) == True)
            
            if not widget_required:
                continue

            row_id = self.layout.rowCount()
            display_name = column_configuration.get("Display", column)
            
            editor = QtWidgets.QCheckBox(display_name)
            self.editors[column] = editor
            self.layout.addWidget(editor, row_id, 1, 1, 1)

    def selectedColumns(self):
        selected_columns = {}
        for column_name, editor in self.editors.items():
            if editor.isChecked() and column_name not in selected_columns.keys():
                column_configuration = self._form_confguration.get(column_name, None)
                if column_configuration:
                    column_configuration = {column_name: column_configuration}
                    selected_columns.update(column_configuration)
        return selected_columns