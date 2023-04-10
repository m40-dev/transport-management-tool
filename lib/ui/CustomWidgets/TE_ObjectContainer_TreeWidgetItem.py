from PyQt6.QtCore import Qt
from lib.xml.object_container import object_container
from lib.ui.CustomWidgets.TemplateEditorListWidget import TemplateEditorListWidgetItem
import copy
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem
from lib.ui.CustomWidgets.TE_Table_TreeWidgetItem import TE_Table_TreeWidgetItem
from lib.ui.CustomWidgets.TE_ObjectContainerData_TreeWidgetItem import TE_ObjectContainerData_TreeWidgetItem


class TE_ObjectContainer_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None, table_name=None):
        super(TE_ObjectContainer_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget, table_name=table_name)

        self.setCheckState(1, Qt.CheckState.Unchecked)  
        self.setText(1, "Delete Residual Objects")
        self.setFlags(Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable |Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsUserCheckable)
        # self.column_data_changed.connect(self.handle_data_change)
        self.object_relations = None
        if isinstance(source_widget, TemplateEditorListWidgetItem):
            object_relations = copy.deepcopy(source_widget.object_relations)
            if object_relations is not None:
                relations_sorted = sorted(object_relations, key=lambda d: (d['ParentTable'],  d['ChildTable'])) 
                self.object_relations = relations_sorted    
            self.refresh()

        if object_data is not None:
            self.list_related_objects()
        
        if object_data is None and xml_object is not None:
            self.load_container_from_xml()

    def set_all_relations_state(self, state):
        if self.object_relations is not None:
            for relation in self.object_relations:
                relation["Relation"] = state
        
            if isinstance(self.xml_object, object_container):
                self.xml_object.relations = self.object_relations

            self.refresh()
            return True
        return False
    
    def set_object_relations(self, relations_data):
        self.object_relations = relations_data
        if isinstance(self.xml_object, object_container):
            self.xml_object.relations = self.object_relations
        self.refresh()

    def load_container_from_xml(self):
        self.setText(0, self.display_name)
        self.object_relations = copy.deepcopy(self.xml_object.xml_object_relations)
        self.xml_object.relations = self.object_relations
        if int(self.xml_object.delete_residuals) > 0:
            self.setCheckState(1, Qt.CheckState.Checked)

        if self.application.ui.AutoLoadCheckBox.isChecked():
            self.load_from_database()

        self.list_related_objects()

    def list_related_objects(self, override=False):
        if not override and not self.application.ui.AutoListObjectsFromDatabaseCheckBox.isChecked():
            return False
        
        if not self.application.db:
            return False
        
        if self.object_data is None:
            self.load_from_database()

        for i in reversed(range(self.childCount())):
            self.removeChild(self.child(i))

        for table_name, results in self.related_objects.items():
            table_display_name = table_name
            if self.application.db:
                table_display_name = self.application.db.table_info.get(table_name, table_name)

            table_widget = TE_Table_TreeWidgetItem(self.application, table_display_name)

            self.addChild(table_widget)
            for selected_object in results:
                selected_object_widget = TE_ObjectContainerData_TreeWidgetItem(self.application, selected_object, table_name=table_name)
                table_widget.addChild(selected_object_widget)
            table_widget.sortChildren(0, Qt.SortOrder.AscendingOrder)
    
    def load_from_database(self):
        if self.xml_object is not None and self.application.db:
            table_name = self.xml_object.table_name
            self.object_data = self.application.db.get_db_object(table_name, self.xml_object.key_columns, "and" )
            
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
            
            """ select all base relations that match the xml relation state, skip relations that are not marked for transport in the database """
            selected_relations, skipped_relations = self.select_referenced_relations(source=self.object_relations, target=db_relations)

            """ select leftover relations where we can match the parent column with the child column """
            selected_relations, skipped_relations = self.select_skipped_relations(skipped_relations, selected_relations, db_relations, match_parent_column=True)
            
            """ select leftover relations where the xml relation matches and do not try to match the parent column anymore (basically include all relations where necessary) """
            selected_relations, skipped_relations = self.select_skipped_relations(skipped_relations, selected_relations, db_relations, match_parent_column=False)
    
            relations_sorted = sorted(db_relations, key=lambda d: (d['ParentTable'],  d['ChildTable'])) 

            """ save final relation data """
            self.object_relations = relations_sorted
            self.xml_object.relations = relations_sorted
    
    def select_skipped_relations(self, skipped_relations, selected_relations, target, match_parent_column=True):
        updated_keys = []
        follow_up_relations = []
        for relation_key, relations in skipped_relations.items():
            for relation in relations:
                relation_table = relation["ChildTable"]
                relation_column = relation["ChildColumn"]
                skipped_key = f"{relation_table}|{relation_column}"
                if skipped_key not in selected_relations.keys():
                    updated_keys.append(relation_key)
                    if relation not in follow_up_relations:
                        follow_up_relations.append(relation)
                    
        return self.select_referenced_relations(source=follow_up_relations, target=target, ignore_initial_state=True, match_parent_column=match_parent_column)

    def select_referenced_relations(self, source, target, ignore_initial_state=False, match_parent_column=True):
        skipped_relations = {}
        selected_relations = {}

        for xml_source_relation in source:
            xml_table = xml_source_relation["ChildTable"]
            xml_column = xml_source_relation["ChildColumn"]
            xml_relation = xml_source_relation["Relation"]

            for db_relation in target:
                db_table = db_relation["ChildTable"]
                db_column = db_relation["ChildColumn"]
                db_parent_column = db_relation["ParentColumn"]
                db_initial_state = db_relation["InitialRelationState"]

                relation_key = f"{db_table}|{db_column}"

                skip_entry = False
                if ignore_initial_state and match_parent_column:
                    if db_table == xml_table and db_column == xml_column and db_parent_column != xml_column:
                        skip_entry = True

                if db_table == xml_table and db_column == xml_column and (db_initial_state > 0 or (ignore_initial_state and not skip_entry)):
                    db_relation["Relation"] = xml_relation
                    
                    if relation_key not in selected_relations.keys():
                        selected_relations[relation_key] = [db_relation]
                        continue
                    if db_relation not in selected_relations[relation_key]:
                        selected_relations[relation_key].append(db_relation)
                        continue
                else:
                    relation_key = f"{xml_table}|{xml_column}"
                    if relation_key not in skipped_relations.keys():
                        skipped_relations[relation_key] = [xml_source_relation]
                        continue

                    if xml_source_relation not in skipped_relations[relation_key]:
                        skipped_relations[relation_key].append(xml_source_relation)
                        
        return selected_relations, skipped_relations

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
            self.list_related_objects()
        
        if isinstance(self.xml_object, object_container):
            self.xml_object.reset_container_relations()

            if self.xml_object.delete_residuals == 1:
                self.setCheckState(1, Qt.CheckState.Checked)
            else:
                self.setCheckState(1, Qt.CheckState.Unchecked)

        self.application.xml_structure_changed.emit()

    def handle_data_change(self, column):
        # print("data change in object container", column)
        status = int(self.checkState(1) == Qt.CheckState.Checked)
        tree_widget = self.treeWidget()

        self.set_delete_residual_objects(status)

        for element in tree_widget.selectedItems():
            if isinstance(element, TE_ObjectContainer_TreeWidgetItem) and element != self:
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
        table_info = self.application.db.table_info.get(self.table_name, None)
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
        if TableRelation in [2, 3, 7] and (self.table_name == ParentTable or self.table_name == ChildTable):
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
        if TableRelation in [1, 3, 5] and (self.table_name == ParentTable or self.table_name == ChildTable):
            # print("FK RELATION")
            # column_value = self.get_value(ChildColumn)
            # if column_value is None:
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
            return True
        else:
            """ Try to follow up later """
            return False

    def reload_referenced_objects(self, source_relation, column_values, currently_selected):
        """ Reload objects which are related to the table and column data with the provided values and add results to the currently selected items """
        if column_values is not None:
            if len(column_values) == 0:
                return False
            
        s_ParentTable = source_relation["ParentTable"]
        s_ParentColumn = source_relation["ParentColumn"]
        s_ChildTable = source_relation["ChildTable"]
        s_ChildColumn = source_relation["ChildColumn"]

        column_value = "', '".join(column_values)
        if self.object_relations is not None:
            for relation in self.object_relations:
                TableRelation = relation["Relation"]
                ParentTable = relation["ParentTable"]
                ParentColumn = relation["ParentColumn"]
                ChildTable = relation["ChildTable"]
                ChildColumn = relation["ChildColumn"]
                
                if TableRelation == 0 or ParentTable == ChildTable:
                    continue

                # if ParentTable == s_ParentTable == self.table_name and ParentColumn == s_ParentColumn and TableRelation in [2, 3, 7]:
                #     print("Reload relation CR for Base Table objects:", relation, column_values, source_relation)
                #     res = self.get_db_objects(ChildTable, ChildColumn, column_value, currently_selected, recursive=False, recursive_key_column=ParentColumn)

                # if ChildTable == s_ChildTable and ChildColumn == s_ChildColumn and TableRelation in [1, 3, 5]:
                #     print("Reload relation FK:", relation, column_values, source_relation )
                #     res = self.get_db_objects(ParentTable, ParentColumn, column_value, currently_selected, recursive=False, recursive_key_column=ChildColumn)
                #     if len(res) > 0:
                #         continue

                if ParentTable == s_ChildTable and TableRelation in [2, 3, 7]:
                    # print("Reload relation CR:", source_relation, column_values, relation )
                    res = self.get_db_objects(ChildTable, ChildColumn, column_value, currently_selected, recursive=False, recursive_key_column=ParentColumn)

                if ParentTable == s_ParentTable and TableRelation in [1, 3]:
                    # print("Reload relation FK:", source_relation, column_values, relation )
                    res = self.get_db_objects(ParentTable, ParentColumn, column_value, currently_selected, recursive=False, recursive_key_column=ChildColumn)

                

    def get_db_objects_values(self, all_objects_dict, table_name, column_name):
        values_list = []
        if table_name in all_objects_dict.keys():
            related_objects = all_objects_dict[table_name]
            for record in related_objects:
                record_columns = self.application.db.get_object_columns(record)
                if column_name in record_columns:
                    column_value = record.__getattribute__(column_name)
                    if column_value is not None:
                        values_list.append(column_value)
        return values_list


    def get_db_objects(self, table_name, query_column, query_values, selected_objects_dict={}, recursive=False, recursive_key_column=None):
        
        query = f"select * from {table_name} where {query_column} in ('{query_values}')"
        
        database_where_clause = self.application.db.get_transport_where_clause(table_name)
        
        if database_where_clause:
            query = f"select * from {table_name} where {query_column} in ('{query_values}') and {database_where_clause}"
        
        query_result = self.application.db.run_db_query(query)

        # print("results:", len(query_result), "query:", query)
        follow_up_values = []
        query_results_list = []
        for db_record in query_result:

            db_object_columns = self.application.db.get_object_columns(db_record)
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
            new_query_results = self.get_db_objects(table_name, query_column, new_query_values, selected_objects_dict, recursive, recursive_key_column)
            for record in new_query_results:
                if record not in query_results_list and record is not None:
                    query_results_list.append(record)
        return query_results_list