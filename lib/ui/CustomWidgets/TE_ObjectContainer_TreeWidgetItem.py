from PyQt6.QtCore import Qt
from lib.xml.object_container import object_container
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
import copy
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem


class TE_ObjectContainer_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_ObjectContainer_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

        self.setCheckState(1, Qt.CheckState.Unchecked)  
        self.setFlags(Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable)
        
        self.object_relations = None
        if isinstance(source_widget, TemplateEditorListWidgetItem):
            object_relations = copy.deepcopy(source_widget.object_relations)
            if object_relations is not None:
                relations_sorted = sorted(object_relations, key=lambda d: (d['ParentTable'],  d['ChildTable'])) 
                self.object_relations = relations_sorted    
            self.refresh()
        
        if object_data is None and xml_object is not None:
            self.load_container_from_xml()

    def load_container_from_xml(self):
        self.setText(0, self.display_name)
        self.object_relations = copy.deepcopy(self.xml_object.xml_object_relations)
        self.xml_object.relations = self.object_relations
        # self.application.load_table_relations(self.object_relations, self)
    
    def load_from_database(self):
        if self.xml_object is not None:
            table_name = self.xml_object.table_name
            self.object_data = self.db.get_db_object(table_name, self.xml_object.key_columns, "and" )
            if len(self.object_data) > 0:
                self.object_data = self.object_data[0]
            db_relations = self.application.get_table_initial_relations(table_name)
            loaded_tables = [table_name]

            for xml_source_relation in self.object_relations:
                xml_table = xml_source_relation["ChildTable"]
                if xml_table not in loaded_tables:
                    loaded_tables.append(xml_table)
                    new_relations = self.application.get_table_initial_relations(xml_table)
                    db_relations = self.application.extend_table_relations(db_relations, new_relations)

            if db_relations is not None:
                for db_relation in db_relations:
                    db_relation["Relation"] = 0

            for xml_source_relation in self.object_relations:
                xml_table = xml_source_relation["ChildTable"]
                xml_column = xml_source_relation["ChildColumn"]
                xml_relation = xml_source_relation["Relation"]

                for db_relation in db_relations:
                    db_table = db_relation["ChildTable"]
                    db_column = db_relation["ChildColumn"]
                    if db_table == xml_table and db_column == xml_column:
                        db_relation["Relation"] = xml_relation
            
            relations_sorted = sorted(db_relations, key=lambda d: (d['ParentTable'],  d['ChildTable'])) 
            self.object_relations = relations_sorted
            self.xml_object.relations = relations_sorted
        self.refresh()

    @property
    def display_name(self):
        if self.xml_object is not None:
            return f"{self.xml_object.table_name} - {self.xml_object.display_name}"
        
    @property
    def search_text(self):
        return self.xml_object.display_name
    
    def refresh(self):
        if self.object_data is not None:
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

        self.set_delete_residual_objects(status)

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

    @property
    def pk_columns(self):
        table_info = self.db.table_info.get(self.objectkey_table, None)
        if table_info is not None:
            return table_info.PKName1, table_info.PKName2
        return None, None

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
                record_columns = self.db.get_object_columns(record)
                if column_name in record_columns:
                    column_value = record.__getattribute__(column_name)
                    if column_value is not None:
                        values_list.append(column_value)
        return values_list


    def get_db_objects(self, table_name, query_column, query_values, selected_objects_dict={}, recursive=False, recursive_key_column=None):

        query = f"select * from {table_name} where {query_column} in ('{query_values}')"
        query_result = self.db.run_db_query(query)

        # print("results:", len(query_result), "query:", query)
        follow_up_values = []
        query_results_list = []
        for db_record in query_result:

            db_object_columns = self.db.get_object_columns(db_record)
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