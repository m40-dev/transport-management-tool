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
                            column_value =  self.get_value(column_name)
                            object_display = object_display.replace(column_name, column_value)
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
    
    @property
    def follow_table(self):
        value = ""
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

    def get_db_object_columns(self, db_row):
        if isinstance(db_row, Row):
            columns = [column[0] for column in db_row.cursor_description]
            return columns
        return []

    @property
    def related_objects(self):
        follow_up_relations = []
        selected_objects = {self.table_name: [self.object_data]}
        if self.object_relations is not None:
            for relation in self.object_relations:
                # Configuration
                status = self.get_relation_objects(relation, selected_objects)
                if not status:
                    follow_up_relations.append(relation)

        print("follow up relations:", follow_up_relations)

        for f_relation in follow_up_relations:
            status = self.get_relation_objects(f_relation, selected_objects)
            if not status:
                print("follow up failed:", f_relation)
        print(selected_objects)
        return selected_objects

    def get_relation_objects(self, relation, selected_objects={}):
        base_object_table = relation["ParentTable"]
        base_object_value_column = relation["ParentColumn"]

        table_name = relation["ChildTable"]
        column_name = relation["ChildColumn"]

        column_value = self.get_value(base_object_value_column)
        print(f"Relation: ", relation)

        if base_object_table != self.table_name and base_object_table in selected_objects.keys():
            query_values_list = []
            for related_object in selected_objects[base_object_table]:
                related_object_columns = self.get_db_object_columns(related_object)
                if base_object_value_column in related_object_columns:
                    base_object_value = related_object.__getattribute__(base_object_value_column)
                    query_values_list.append(str(base_object_value))
            column_value = "', '".join(query_values_list)
            print(column_value)

        query_results = self.get_db_objects(table_name, column_name, column_value)
        
        for db_record in query_results:
            if table_name not in selected_objects.keys():
                selected_objects[table_name] = [db_record]
            else:
                if db_record not in selected_objects[table_name]:
                    selected_objects[table_name].append(db_record)
        return True

    def get_db_objects(self, table_name, query_column, query_values):
        selected_objects = []
        query = f"select * from {table_name} where {query_column} in ('{query_values}')"

        query_result = self.db_connection.run_db_query(query)
        for row in query_result:
            selected_objects.append(row)
        print("results:", len(selected_objects), "query:", query)
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


class TE_RelationColumn_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_RelationColumn_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

    @property
    def display_name(self):
        display = None
        if isinstance(self.object_data, dict):
            table_name = self.object_data.get("table_name", "")
            column_name = self.object_data.get("column_name", "")
            relation_type = self.object_data.get("relation_type", "")
            follow_table = self.object_data.get("follow_table", "")
            follow_column = self.object_data.get("follow_column", "")
            display = f"{relation_type}: {column_name} -> {follow_table}"

        if isinstance(self.object_data, Row):
            if self.objectkey_table == "DialogColumn":
                display = f"{self.object_data.ColumnName} - ({self.object_data.Caption})"
        
        if display is None:
            display = "Column without display name"
        return display