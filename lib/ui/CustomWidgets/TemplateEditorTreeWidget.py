from PyQt6.QtWidgets import  QWidget, QGridLayout, QTreeWidgetItem
from PyQt6.QtCore import Qt
from pyodbc import Row
from lib.xml.transport_template import transport_template_custom_object, object_container
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
        if isinstance(self.xml_object, transport_template_custom_object):
            if self.xml_object.delete_object():
                return True
            else:
                return False           

        if isinstance(self, TemplateEditorTreeWidgetItem):
            for i in reversed(range(self.childCount())):
                child_item = self.child(i)
                if isinstance(child_item, TE_RelationColumn_TreeWidgetItem):
                    child_item.delete_relation(child_item.object_data)
            if self.source_widget is not None:
                self.source_widget.refresh()

        if isinstance(self, TE_RelationColumn_TreeWidgetItem) and self.object_relations is not None:
            self.delete_relation(self.object_data)
            
        return True

    def delete_relation(self, relation):
        if relation in self.source_widget.object_relations:
            self.source_widget.object_relations.remove(relation)
        return True


    def refresh(self):
        self.setDisplayName(self.display_name)
        if isinstance(self.xml_object, object_container):
            self.xml_object.reset_container_relations()
            self.application.list_related_objects(self)

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
            if self.table_name== "DialogTable":
                value = self.object_data.TableName
        return value

    @property
    def delete_residual_objects(self):
        #TODO: add handling for the value based on the UI selection
        return "1"

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

        for f_relation in follow_up_relations:
            status = self.get_relation_objects(f_relation, selected_objects)
            if not status:
                print("follow up failed:", f_relation)

        return selected_objects

    def get_relation_objects(self, relation, selected_objects={}):
        BaseTable = relation["TableGroup"]
        TableRelation = relation["Relation"]
        ParentTable = relation["ParentTable"]
        ParentColumn = relation["ParentColumn"]

        ChildTable = relation["ChildTable"]
        ChildColumn = relation["ChildColumn"]

        recursive = False
        if TableRelation in [2, 3]:
            recursive = True
        column_value = ""
        values_list = []
        # print(f"Relation: ", relation)

        if BaseTable == ParentTable and ParentTable == self.table_name:
            # column_value = self.get_value(ParentColumn)
            values_list = self.get_db_objects_values(selected_objects, ParentTable, ParentColumn)
            if len(values_list) > 0:
                column_value = "', '".join(values_list)
                self.get_db_objects(ChildTable, ChildColumn, column_value, selected_objects, recursive, ParentColumn)

        elif BaseTable == ChildTable and ChildTable == self.table_name:
            # column_value = self.get_value(ChildColumn)
            values_list = self.get_db_objects_values(selected_objects, ChildTable, ChildColumn)
            if len(values_list) > 0:
                column_value = "', '".join(values_list)
            self.get_db_objects(ParentTable, ParentColumn, column_value, selected_objects, recursive, ChildColumn)
        else:
            """ foreign table relation """
            values_list = []
            if BaseTable == ParentTable:
                values_list = self.get_db_objects_values(selected_objects, ParentTable, ParentColumn)
                if len(values_list) > 0:
                    column_value = "', '".join(values_list)
                    self.get_db_objects(ChildTable, ChildColumn, column_value, selected_objects, recursive, ParentColumn)
                else:
                    print("Parent table data not found:", ParentTable)

            if BaseTable == ChildTable:
                values_list = self.get_db_objects_values(selected_objects, ChildTable, ChildColumn)
                if len(values_list) > 0:
                    column_value = "', '".join(values_list)
                    self.get_db_objects(ParentTable, ParentColumn, column_value, selected_objects, recursive, ChildColumn)
                else:
                    print("Parent table data not found:", ParentTable)
        return True

    def get_db_objects_values(self, all_objects_dict, table_name, column_name):
        values_list = []
        if table_name in all_objects_dict.keys():
            related_objects = all_objects_dict[table_name]
            for record in related_objects:
                record_columns = self.get_db_object_columns(record)
                if column_name in record_columns:
                    column_value = record.__getattribute__(column_name)
                    if column_value is not None:
                        values_list.append(column_value)
        return values_list


    def get_db_objects(self, table_name, query_column, query_values, selected_objects_dict={}, recursive=False, recursive_key_column=None):

        query = f"select * from {table_name} where {query_column} in ('{query_values}')"
        query_result = self.db_connection.run_db_query(query)

        # print("results:", len(query_result), "query:", query)
        follow_up_values = []
        for db_record in query_result:
            if table_name not in selected_objects_dict.keys():
                selected_objects_dict[table_name] = [db_record]
            else:
                if db_record not in selected_objects_dict[table_name]:
                    selected_objects_dict[table_name].append(db_record)
            if recursive:
                db_object_columns = self.get_db_object_columns(db_record)
                if recursive_key_column in db_object_columns:
                    follow_up_values.append(db_record.__getattribute__(recursive_key_column))

        new_query_values = "', '".join(follow_up_values)
        if recursive and len(follow_up_values) > 0 and new_query_values != query_values:
            self.get_db_objects(table_name, query_column, new_query_values, selected_objects_dict, recursive)
        return selected_objects_dict


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
            if self.ParentTable == self.TableGroup:
                display = f"{self.follow_table} -> {self.follow_column} <-> {self.ParentTable}"
            else:
                display = f"{self.follow_table} - > {self.follow_column} <-> {self.follow_table}"

        if isinstance(self.object_data, Row):
            if self.objectkey_table == "DialogColumn":
                display = f"{self.object_data.Caption} - ({self.object_data.ColumnName})"
        
        if display is None:
            display = "Column without display name"

        return display

    @property
    def follow_table(self):
        if self.ParentTable == self.TableGroup:
            return self.ChildTable
        return self.ParentTable
    
    @property
    def follow_column(self):
        if self.ParentTable == self.TableGroup:
            return self.ParentColumn
        return self.ChildColumn

    @property
    def ChildTable(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ChildTable", "")

    @property
    def ChildColumn(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ChildColumn", "")

    @property
    def ParentTable(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ParentTable", "")
            
    @property
    def ParentColumn(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("ParentColumn", "")
    
    @property
    def TableGroup(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("TableGroup", "")
        