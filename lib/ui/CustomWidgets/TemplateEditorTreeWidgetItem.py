from PyQt6.QtWidgets import  QTreeWidgetItem
from PyQt6.QtCore import Qt
from pyodbc import Row
from lib.xml.transport_template_custom_object import transport_template_custom_object
import copy
import re

class TemplateEditorTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None, table_name=None):
        super(TemplateEditorTreeWidgetItem, self).__init__()

        self.application = application
        self.xml_object = xml_object
        self.object_data = object_data
        self.source_widget = source_widget
        self.source_table = table_name
        self.object_relations = None

        # self.refresh()

    def deleteObject(self):
        if isinstance(self.xml_object, transport_template_custom_object):
            if self.xml_object.delete_object():
                return True
            else:
                return False           
        return True

    def refresh(self):
        self.setDisplayName(self.display_name)

    @property
    def tooltipText(self):
        return f"{str(self.data.tag)}: {str(self.data.attrib)}. {str(self.data.text)}"
    
    @property
    def xobjectkey(self):
        XObjectKey = None
        if isinstance(self.object_data, Row):
            if "XObjectKey" in self.object_columns:
                XObjectKey = self.object_data.XObjectKey
        return XObjectKey

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
    def table_name(self):
        if self.source_table is not None:            
            return self.source_table
        return self.objectkey_table
    
    @property
    def object_columns(self):
        return self.application.db.get_object_columns(self.object_data)

    @property
    def table_display_pattern(self):
        table_info = self.application.db.table_info.get(self.table_name, None)
        if table_info is not None:
            return table_info.DisplayPattern
        return None

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, dict):
            display = self.object_data.get("Name", display)

        if isinstance(self.object_data, Row):
            if self.table_display_pattern is not None and display is None:
                object_display = self.table_display_pattern.upper()
                if "%" in self.table_display_pattern:
                    for column_name in self.object_columns:
                        if column_name.upper() in object_display:
                            column_value =  self.object_data.__getattribute__(column_name)
                            if column_value is None:
                                column_value = ""
                            object_display = object_display.replace(column_name.upper(), column_value)
                    object_display = object_display.replace("%", "")
                display = f"{self.objectkey_table} - ({object_display})"
        
        if display is None:
            display = f"{self.objectkey_table} - ({self.xobjectkey})"
        
        return display

    def setDisplayName(self, display_text):
        self.setText(0, display_text)

    def get_value(self, column_name):
        value = ""
        if isinstance(self.object_data, dict):
            value = self.object_data.get(column_name, "")

        if isinstance(self.object_data, Row):
            if column_name in self.object_columns:
                value = self.object_data.__getattribute__(column_name)

        if value is None:
            value = ""
        return value
    


    def handle_data_change(self, column):
        pass

