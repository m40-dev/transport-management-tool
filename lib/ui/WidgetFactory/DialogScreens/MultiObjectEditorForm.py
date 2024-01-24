from PyQt6 import QtCore, QtWidgets, QtGui
from .MessageBox import MsgBox
from .CustomDialogWindow import CustomDialogWindow

class MultiObjectEditorForm(CustomDialogWindow):

    def __init__(self, application, configuration_class, dialog_name="Data Editor - Column Selection", form_configuration=None):
        super(MultiObjectEditorForm, self).__init__(application=application, dialog_name=dialog_name)

        self.application = application
        self.configuration_class = configuration_class
        self._form_confguration = self.application.getConfigurationParameters(configuration_class)
        if form_configuration is not None:
            self._form_confguration = form_configuration
        self._form_data = {}
        self._base_object_data = None
        self.setMinimumSize(400, 400)

        self.setWindowTitle(f"{self.application.application_name} - {dialog_name}") 

        self.editors = {}
        self.setup_form()
       

    def setup_form(self):
        description_label = QtWidgets.QLabel("Select Columns to be updated in bulk for all selected items.\nOnly same object class items will be updated.")
        self.form_layout.addWidget(description_label, self.form_layout.rowCount(), 0, 1, 2, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        itemcount = len(self._form_confguration.items())
        rowcount_restart = self.form_layout.rowCount()
        row_break = (itemcount / 2) + rowcount_restart
        column_id = 0
        row_id = self.form_layout.rowCount()
        for column, column_configuration in self._form_confguration.items():
            widget_required = (column_configuration.get("ShowInEditor", True) == True)
            
            if not widget_required:
                continue

            display_name = column_configuration.get("Display", column)
            
            editor = QtWidgets.QCheckBox(display_name)
            self.editors[column] = editor
            
            self.form_layout.addWidget(editor, row_id, column_id)
            row_id += 1
            if row_id >= row_break:
                row_id = rowcount_restart
                column_id += 1

        self.form_layout.setRowStretch(self.form_layout.rowCount(), 2)
        

    def selectedColumns(self):
        selected_columns = {}
        for column_name, editor in self.editors.items():
            if editor.isChecked() and column_name not in selected_columns.keys():
                column_configuration = self._form_confguration.get(column_name, None)
                if column_configuration:
                    column_configuration = {column_name: column_configuration}
                    selected_columns.update(column_configuration)
        return selected_columns