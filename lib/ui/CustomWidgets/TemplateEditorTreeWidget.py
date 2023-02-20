from PyQt6.QtWidgets import  QWidget, QGridLayout, QTreeWidgetItem
from PyQt6.QtCore import Qt
from pyodbc import Row
from lib.xml.transport_template import transport_template_custom_object
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
import copy
import re

class TemplateEditorTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TemplateEditorTreeWidgetItem, self).__init__()

        self.application = application
        self.db_connection = self.application.db_connection
        self.xml_object = xml_object
        self.object_data = object_data
        self.source_widget = source_widget
        self.object_relations = None

        if isinstance(source_widget, TemplateEditorListWidgetItem):
            self.object_relations = copy.deepcopy(source_widget.object_relations)

        self.refresh()

    def deleteObject(self):
        if self.xml_object.delete_object():
            return True
        return False

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
    def object_columns(self):
        if isinstance(self.object_data, Row):
            columns = [column[0] for column in self.object_data.cursor_description]
            return columns
        return []

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

    def setDisplayName(self, display_text):
        self.setText(0, display_text)

    def get_value(self, column_name):
        if isinstance(self.object_data, dict):
            value = self.object_data.get(column_name, None)

        if isinstance(self.object_data, Row):
            value = self.object_data.__getattribute__(column_name)
        
        if value is None:
            return ""
        return value
    
    @property
    def follow_table(self):
        if isinstance(self.object_data, dict):
            value = self.object_data.get("follow_table", None)

        if isinstance(self.object_data, Row):
            if self.table_name == "DialogTable":
                value = self.object_data.TableName
        return value

    @property
    def pk_columns(self):
        db_table_info = self.application.db_table_info.get(self.objectkey_table, None)
        if db_table_info is not None:
            return db_table_info.PKName1, db_table_info.PKName2
        return None, None

    @property
    def related_objects(self):
        selected_objects = {self.table_name: [self.object_data]}
        if self.object_relations is not None:
            for relation_type, relation_tables_dict in self.object_relations.items():
                for table_name, relation_columns_list in relation_tables_dict.items():
                    for relation in relation_columns_list:
                        relation_type = relation["relation_type"]
                        if relation_type == "FK":
                            table_name = relation["follow_table"]
                            column_name = relation["follow_column"]
                            if column_name in self.object_columns:
                                query = f"select * from {table_name} where {column_name} = '{self.get_value(column_name)}'"
                        else:
                            table_name = relation["table_name"]
                            column_name = relation["column_name"]
                            if column_name in self.object_columns:
                                query = f"select * from {table_name} where {column_name} = '{self.get_value(column_name)}'"
                        # print("Relation: ", relation, "Query: ", query)
                        query_result = self.db_connection.run_db_query(query)
                        for row in query_result:
                            if table_name not in selected_objects.keys():
                                selected_objects[table_name] = [row]
                            else:
                                if row not in selected_objects[table_name]:
                                    selected_objects[table_name].append(row)

        return selected_objects


class TE_Table_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_Table_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, Row):
            if self.objectkey_table == "DialogTable":
                display = f"{self.object_data.TableName} - ({self.object_data.DisplayName})"
        if display is None:
            display = "Table without display name"
        return display


class TE_Column_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_Column_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, dict):
            table_name = self.object_data.get("table_name", "")
            column_name = self.object_data.get("column_name", "")
            relation_type = self.object_data.get("relation_type", "")
            display = f"{relation_type}: {column_name}"

        if isinstance(self.object_data, Row):
            if self.objectkey_table == "DialogColumn":
                display = f"{self.object_data.ColumnName} - ({self.object_data.Caption})"
        
        if display is None:
            display = "Column without display name"
        return display