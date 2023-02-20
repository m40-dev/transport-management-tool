from PyQt6.QtWidgets import  QWidget, QGridLayout, QListWidgetItem
from PyQt6.QtCore import Qt
from pyodbc import Row
from lib.xml.transport_template import transport_template_custom_object
import copy

import re

class TemplateEditorListWidgetItem(QListWidgetItem):
    def __init__(self, application, object_data, xml_object=None):
        super(TemplateEditorListWidgetItem, self).__init__()

        self.application = application
        self.xml_object = xml_object
        self.object_data = object_data
        self.object_relations = copy.deepcopy(self.application.db_table_relations.get(self.table_name, None))
        self.refresh()

    def deleteObject(self):
        if self.xml_object.delete_object():
            self.parent = None
            self.deleteLater()

    def refresh(self):
        self.setDisplayName(self.display_name)

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
        db_table_info = self.application.db_table_info.get(self.objectkey_table, None)
        if db_table_info is not None:
            return db_table_info.DisplayPattern
        return None
    
    @property
    def table_name(self):
        return self.objectkey_table

    @property
    def pk_columns(self):
        db_table_info = self.application.db_table_info.get(self.objectkey_table, None)
        if db_table_info is not None:
            return db_table_info.PKName1, db_table_info.PKName2
        return None, None

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, dict):
            display = self.object_data.get("Name", display)

        if isinstance(self.object_data, Row):
            if self.table_display_pattern is not None and display is None:
                object_display = self.table_display_pattern
                if "%" in self.table_display_pattern:
                    for column_name in self.object_columns:
                        if column_name in object_display:
                            column_value =  self.object_data.__getattribute__(column_name)
                            if column_value is None:
                                column_value = ""
                            object_display = object_display.replace(column_name, column_value)
                    object_display = object_display.replace("%", "")
                display = f"{self.objectkey_table} - ({object_display})"
        if display is None:
            display = f"{self.objectkey_table} - ({self.xobjectkey})"
        return display

    @property
    def delete_residual_objects(self):
        #TODO: add handling for the value based on the UI selection
        return "1"

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
    