from PyQt6.QtWidgets import  QListWidgetItem
from PyQt6.QtCore import Qt
from pyodbc import Row
import re

class TemplateEditorListWidgetItem(QListWidgetItem):
    def __init__(self, application, object_data, xml_object=None):
        super(TemplateEditorListWidgetItem, self).__init__()

        self.application = application
        self.xml_object = xml_object
        self.object_data = object_data
        self.object_relations = None
        self.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        self.refresh()

        self.set_object_relations(self.application.get_table_initial_relations(self.table_name))

    def set_object_relations(self, object_relations_list):
        self.object_relations = object_relations_list

    def deleteObject(self):
        if self.xml_object.delete_object():
            self.parent = None
            self.deleteLater()

    def refresh(self):
        self.setDisplayName(self.display_name)

    def set_relation_state(self, changed_relation):
        
        if self.object_relations is not None:
            for relation in self.object_relations:
                if (relation["ParentTable"] == changed_relation["ParentTable"] and relation["ChildTable"] == changed_relation["ChildTable"]
                    and relation["ParentColumn"] == changed_relation["ParentColumn"] and relation["ChildColumn"] == changed_relation["ChildColumn"]
                    ):
                    relation["Relation"] = changed_relation["Relation"]
                    # print("update relation state:", changed_relation)

    @property
    def tooltipText(self):
        return f"{str(self.data.tag)}: {str(self.data.attrib)}. {str(self.data.text)}"
    
    @property
    def xobjectkey(self):
        XObjectKey = None
        if isinstance(self.object_data, Row):
            columns = [column[0] for column in self.object_data.cursor_description]
            if "XObjectKey" in columns:
                XObjectKey = self.object_data.XObjectKey
        return XObjectKey

    @property
    def object_columns(self):
        if isinstance(self.object_data, Row):
            columns = [column[0] for column in self.object_data.cursor_description]
            return columns
        return []

    @property
    def objectkey_table(self):
        table_name = None
        regex = r"<T>(.*?)</T>"
        if self.xobjectkey is not None:
            match = re.search(regex, self.xobjectkey)
            if match:
                table_name = match.group(1)
        return table_name

    @property
    def table_display_pattern(self):
        table_info = self.application.db.table_info.get(self.objectkey_table, None)
        if table_info is not None:
            return table_info.DisplayPattern
        return None
    
    @property
    def table_name(self):
        return self.objectkey_table

    @property
    def pk_columns(self):
        table_info = self.application.db.table_info.get(self.objectkey_table, None)
        if table_info is not None:
            return table_info.PKName1, table_info.PKName2
        return None, None

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, dict):
            display = self.object_data.get("Name", display)
        
        if isinstance(self.object_data, Row):
            if self.objectkey_table == "DialogTable":
                display = f"{self.object_data.TableName} - ({self.object_data.DisplayName})"
                return display
            if self.objectkey_table == "DialogColumn":
                display = f"{self.object_data.ColumnName} - ({self.object_data.Caption})"
                return display
            
        if isinstance(self.object_data, Row):
            if self.table_display_pattern is not None and display is None:
                object_display = self.table_display_pattern
                if "%" in self.table_display_pattern:
                    for column_name in self.object_columns:
                        if column_name in object_display:
                            column_value =  self.object_data.__getattribute__(column_name)
                            if column_value is None:
                                column_value = ""
                            object_display = object_display.replace(column_name, str(column_value))
                    object_display = object_display.replace("%", "")
                display = f"{self.objectkey_table} - ({object_display})"
        if display is None:
            display = f"{self.objectkey_table} - ({self.xobjectkey})"
        return display

    @property
    def delete_residual_objects(self):
        return str(int(self.application.ui.DeleteResidualCheckBox.isChecked()))

    def setDisplayName(self, display_text):
        self.setText(display_text)

    def get_value(self, column_name):

        if isinstance(self.object_data, dict):
            value = self.object_data.get(column_name, None)

        if isinstance(self.object_data, Row):
            value = self.object_data.__getattribute__(column_name)
        
        if value is None:
            return ""
        return value
    