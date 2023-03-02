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
                        if column_name.upper() in self.table_display_pattern.upper():
                            column_value =  str(self.get_value(column_name))
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
        return str(int(self.application.ui.DeleteResidualCheckBox.isChecked()))

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
                if relation["Relation"] > 0:
                    status = self.get_relation_objects(relation, selected_objects)
                    if not status:
                        follow_up_relations.append(relation)

        for f_relation in follow_up_relations:
            status = self.get_relation_objects(f_relation, selected_objects)
            if not status:
                # print("follow up failed:", f_relation)
                pass

        return selected_objects

    def get_relation_objects(self, relation, selected_objects={}):
        BaseTable = relation["TableGroup"]
        TableRelation = relation["Relation"]
        ParentTable = relation["ParentTable"]
        ParentColumn = relation["ParentColumn"]

        ChildTable = relation["ChildTable"]
        ChildColumn = relation["ChildColumn"]

        recursive = False
        if ParentTable == ChildTable:
            recursive = True

        column_value = ""
        values_list = []
        total_query_results = []
        query_results = []
        # print(f"Relation: ", relation)

        #CR Relation
        if TableRelation in [2, 3, 7]:
            # print("CR RELATION")
            # column_value = self.get_value(ChildColumn)
            values_list = self.get_db_objects_values(selected_objects, ParentTable, ParentColumn)
            if len(values_list) > 0:
                column_value = "', '".join(values_list)
                query_results = self.get_db_objects(ChildTable, ChildColumn, column_value, selected_objects, recursive, ParentColumn)

            if len(query_results) > 0:
                total_query_results += query_results
                # print("reload referenced objects", ChildTable, query_results)
                self.reload_referenced_objects(relation, query_results, selected_objects)

        #FK Relation
        if TableRelation in [1, 3, 5]:
            # print("FK RELATION")
            column_value = self.get_value(ChildColumn)
            if column_value is None:
                values_list = self.get_db_objects_values(selected_objects, ChildTable, ChildColumn)
                if len(values_list) > 0:
                    column_value = "', '".join(values_list)
            # print("column value:", column_value)
            if column_value is not None and column_value.strip() != "":
                query_results = self.get_db_objects(ParentTable, ParentColumn, column_value, selected_objects, recursive, ChildColumn)
                # print("found results", ParentTable, query_results)
                if len(query_results) > 0:
                    # print("reload referenced objects", ParentTable, query_results)
                    total_query_results += query_results
                    self.reload_referenced_objects(relation, query_results, selected_objects)

        if self.table_name != ParentTable and self.table_name != ChildTable:
            """ foreign table relation """
            if TableRelation in [2, 3, 7]:
                # print("Foreign CR RELATION")
                values_list = self.get_db_objects_values(selected_objects, ParentTable, ParentColumn)
                if len(values_list) > 0:
                    column_value = "', '".join(values_list)
                    query_results = self.get_db_objects(ChildTable, ChildColumn, column_value, selected_objects, recursive, ParentColumn)
                    if len(query_results) > 0:
                        total_query_results += query_results
                        # print("reload referenced objects", ChildTable, query_results)
                        self.reload_referenced_objects(relation, query_results, selected_objects)
    
            if TableRelation in [1, 3, 5]:
                # print("Foreign FK RELATION")
                values_list = self.get_db_objects_values(selected_objects, ChildTable, ChildColumn)
                if len(values_list) > 0:
                    column_value = "', '".join(values_list)
                    recursive = False
                    query_results = self.get_db_objects(ParentTable, ParentColumn, column_value, selected_objects, recursive, ChildColumn)
                    if len(query_results) > 0:
                        total_query_results += query_results
                        # print("reload referenced objects", ParentTable, ParentColumn, query_results)
                        self.reload_referenced_objects(relation, query_results, selected_objects)
        if len(total_query_results) > 0:
            # print("total relation results:", relation, total_query_results)
            return True
        else:
            """ Try to follow up later """
            return False

    def reload_referenced_objects(self, source_relation, column_values, currently_selected):
        """ Reload objects which are related to the table and column data with the provided values and add results to the currently selected items """
        if column_values is not None:
            if len(column_values) == 0:
                return False

        column_value = "', '".join(column_values)
        if self.object_relations is not None:
            for relation in self.object_relations:
                TableRelation = relation["Relation"]
                BaseTable = relation["TableGroup"]
                ParentTable = relation["ParentTable"]
                ParentColumn = relation["ParentColumn"]
                ChildTable = relation["ChildTable"]
                ChildColumn = relation["ChildColumn"]

                s_ParentTable = source_relation["ParentTable"]
                s_ParentColumn = source_relation["ParentColumn"]
                s_ChildTable = source_relation["ChildTable"]
                s_ChildColumn = source_relation["ChildColumn"]
                
                if TableRelation == 0 or ParentTable == ChildTable:
                    continue

                if ParentTable == s_ParentTable == self.table_name and ParentColumn == s_ParentColumn and TableRelation in [2, 3, 7]:
                    # print("Reload relation CR for Base Table objects:", relation, column_values, source_relation)
                    res = self.get_db_objects(ChildTable, ChildColumn, column_value, currently_selected, recursive=False, recursive_key_column=ParentColumn)

                if ChildTable == s_ChildTable and ChildColumn == s_ChildColumn and TableRelation in [1, 3, 5]:
                    # print("Reload relation FK:", relation, column_values, source_relation )
                    res = self.get_db_objects(ParentTable, ParentColumn, column_value, currently_selected, recursive=False, recursive_key_column=ChildColumn)
                    if len(res) > 0:
                        continue

                if ParentTable == s_ParentTable and ParentColumn == s_ParentColumn and TableRelation in [2, 3, 7]:
                    # print("Reload relation CR:", source_relation, column_values, relation )
                    res = self.get_db_objects(ChildTable, ChildColumn, column_value, currently_selected, recursive=False, recursive_key_column=ParentColumn)


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
        query_results_list = []
        for db_record in query_result:

            db_object_columns = self.get_db_object_columns(db_record)
            query_column_value =  db_record.__getattribute__(query_column)
            
            # if recursive_key_column is not None and recursive_key_column in db_object_columns:
            #     value =  db_record.__getattribute__(recursive_key_column)
            #     if value is not None and value not in query_results_list:
            #         query_results_list.append(value)
            
            if query_column_value is not None and query_column_value not in query_results_list:
                query_results_list.append(query_column_value)

            if table_name not in selected_objects_dict.keys():
                selected_objects_dict[table_name] = [db_record]
            else:
                if db_record not in selected_objects_dict[table_name]:
                    selected_objects_dict[table_name].append(db_record)

            if recursive and recursive_key_column in db_object_columns:
                value =  db_record.__getattribute__(recursive_key_column)
                if value is not None and value not in follow_up_values:
                    follow_up_values.append(value)
                    query_results_list.append(value)

        new_query_values = "', '".join(follow_up_values)
        
        if recursive and len(follow_up_values) > 0 and new_query_values != query_values:
            new_query_results = self.get_db_objects(table_name, query_column, new_query_values, selected_objects_dict, recursive)
            for record in new_query_results:
                if record not in query_results_list and record is not None:
                    query_results_list.append(record)
        return query_results_list

    def handle_data_change(self, column):
        pass

    def get_table_display(self, table_name):
        db_table_info = self.application.db_table_info.get(table_name, None)
        if db_table_info is not None:
            return db_table_info.DisplayName


class TE_Table_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_Table_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)
        
        self.setFlags(Qt.ItemFlag.NoItemFlags)
        self.setFlags(Qt.ItemFlag.ItemIsEnabled)

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

        self.setFlags(self.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(1, Qt.CheckState.Unchecked)
        self.setCheckState(2, Qt.CheckState.Unchecked)
        self.setCheckState(3, Qt.CheckState.Unchecked)
       
        if self.auto_select_default or isinstance(source_widget, TE_ObjectContainer_TreeWidgetItem):
            self.update_relation_satus()
        
        if not self.auto_select_default and isinstance(source_widget, TemplateEditorListWidgetItem):
            self.set_relation_state(0)

    @property
    def auto_select_default(self):
        return self.application.ui.SelectWithDatabaseModelCheckBox.isChecked()

    @property
    def display_name(self):
        display = None

        if isinstance(self.object_data, dict):
            if self.ParentTable == self.TableGroup and self.ParentTable == self.source_widget.table_name:
                caption = self.get_table_display(self.follow_table)
                display = f"{self.follow_column} << - {self.follow_table} ({caption})"
            else:
                caption = self.get_table_display(self.follow_table)
                display = f"{self.follow_column} - >> {self.follow_table} ({caption})"
        
        if display is None:
            display = "Relation Column without display name"
        return display

    @property
    def follow_table(self):
        if self.TableGroup == self.ParentTable == self.source_widget.table_name:
            return self.ChildTable
        return self.ParentTable
    
    @property
    def follow_column(self):
        return self.ChildColumn

    @property
    def Relation(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("Relation", "0")

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

    @property
    def InitialRelationState(self):
        if isinstance(self.object_data, dict):
            return self.object_data.get("InitialRelationState", 0)
        
    def set_relation_state(self, relation):
        self.object_data["Relation"] = relation

        if isinstance(self.source_widget, TemplateEditorTreeWidgetItem):
            self.source_widget.refresh()
        self.update_relation_satus()

    def show_relation(self, state):
        if self.InitialRelationState == 0:
            self.setHidden(not bool(state))
    
    def select_relations_using_db_model(self, state):
        if bool(state):
            self.set_relation_state(self.InitialRelationState)
        else:
            self.set_relation_state(0)

    def update_relation_satus(self):
        if self.Relation:
            if self.Relation in [1, 3, 5, 7]:
                self.setCheckState(1, Qt.CheckState.Checked)
            else:
                self.setCheckState(1, Qt.CheckState.Unchecked)
            
            if self.Relation in [2, 3, 7]:
                self.setCheckState(2, Qt.CheckState.Checked)
            else:
                self.setCheckState(2, Qt.CheckState.Unchecked)
            
            if self.Relation > 3:
                self.setCheckState(3, Qt.CheckState.Checked)
            else:
                self.setCheckState(3, Qt.CheckState.Unchecked)
        else:
            self.setCheckState(1, Qt.CheckState.Unchecked)
            self.setCheckState(2, Qt.CheckState.Unchecked)
            self.setCheckState(3, Qt.CheckState.Unchecked)
    
    def get_relation_state(self):
        relation = ""
        for i in reversed(range(1, 4)):
            relation += str(int(self.checkState(i) == Qt.CheckState.Checked))
        return self.binary2int(int(relation))

    def handle_data_change(self, column):
        # print("relation change:", self.object_data)
        status = self.get_relation_state()
        self.set_relation_state(status)
        tree_widget = self.treeWidget()
        column_state = self.checkState(column)
        for element in tree_widget.selectedItems():
            if isinstance(element, TE_RelationColumn_TreeWidgetItem):
                element.setCheckState(column, column_state)
    
    def binary2int(self, binary): 
        int_val, i, n = 0, 0, 0
        while(binary != 0): 
            a = binary % 10
            int_val = int_val + a * pow(2, i) 
            binary = binary // 10
            i += 1
        return int_val


class TE_ObjectContainer_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_ObjectContainer_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

        # self.setFlags(self.flags() | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsUserCheckable)
        self.setCheckState(1, Qt.CheckState.Unchecked)  
        self.set_delete_residual_objects(str(int(self.application.ui.DeleteResidualCheckBox.isChecked())))
        self.setFlags(Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable)
        
        self.object_relations = None
        if isinstance(source_widget, TemplateEditorListWidgetItem):
            object_relations = copy.deepcopy(source_widget.object_relations)
            if object_relations is not None:
                relations_sorted = sorted(object_relations, key=lambda d: (d['ParentTable'],  d['ChildTable'])) 
                self.object_relations = relations_sorted      
        self.refresh()

    
    def refresh(self):
        TemplateEditorTreeWidgetItem.refresh(self)
        self.application.list_related_objects(self)
        if isinstance(self.xml_object, object_container):
            self.xml_object.reset_container_relations()

            if self.xml_object.delete_residuals == 1:
                self.setCheckState(1, Qt.CheckState.Checked)
            else:
                self.setCheckState(1, Qt.CheckState.Unchecked)
        self.application.load_xml_preview()

    def handle_data_change(self, column):
        status = int(self.checkState(1) == Qt.CheckState.Checked)
        tree_widget = self.treeWidget()

        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem):
                self.set_delete_residual_objects(status)
                element.setCheckState(column, self.checkState(column))

    @property
    def delete_residual_objects(self):
        return str(int(self.checkState(1) == Qt.CheckState.Checked))
    
    def set_delete_residual_objects(self, state):
        if isinstance(self.xml_object, object_container):
            self.xml_object.set_delete_residuals(state)
        # self.refresh()

class TE_TransportTask_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_TransportTask_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

class TE_ObjectContainerData_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_ObjectContainerData_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)
        self.setFlags(Qt.ItemFlag.NoItemFlags)