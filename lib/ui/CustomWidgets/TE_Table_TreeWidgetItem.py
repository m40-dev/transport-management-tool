from PyQt6.QtCore import Qt
from pyodbc import Row
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem


class TE_Table_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_Table_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)
        
        self.setFlags(Qt.ItemFlag.NoItemFlags)
        self.setFlags(Qt.ItemFlag.ItemIsEnabled)
        self.refresh()

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, Row):
            if self.objectkey_table == "DialogTable":
                display = f"{self.object_data.TableName} - ({self.object_data.DisplayName})"
        if display is None:
            display = "Table without display name"
        return display

    @property
    def follow_table(self):
        value = ""
        if isinstance(self.object_data, Row):
            if self.table_name== "DialogTable":
                value = self.object_data.TableName
        return value