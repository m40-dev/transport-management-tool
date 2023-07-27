import uuid, re
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from copy import deepcopy
from lxml.etree import _Element, _Comment, Element, fromstring
from pyodbc import Row
from .xml_object_definitions import *

FILTER_MIN_LEN = 1

class XMLDataItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, application, object_class="XMLDataItem", object_data=None, xml_custom_object=None, parent=None, model_reference=None):
        super().__init__(parent=parent)
        self.application = application
        self.model_reference = model_reference
        self.object_data = None
        self._xml_data = xml_custom_object
        self.object_relations = []
        self._object_class = object_class
        self._parent = parent
        self._children = []
        self._filtered_children = []
        self._previous_xml_data = None
        self._is_saved = True
        self._filter_match = True
        self.filter_string = ""
        self._display = ""
        self._description = ""
        self._uid = str(uuid.uuid4())

        if self.object_data is None and self._xml_data is not None:
            self.loadDataFromXML()
            
        if xml_custom_object:
            children = xml_custom_object.children()
            if children:
                self.loadChildren(children)
        
        self.dataDropped.connect(self.itemDataDropped)
        self.locationChanged.connect(self.itemLocationChanged)
      
    
    @property
    def table_name(self):
        if self._xml_data is not None:            
            return self._xml_data.table_name
    
    def itemDataDropped(self, source_dict):
        # print("foreign model object dropped", source_dict.get("objectclass", None), self.object_class)
        pass

    def itemLocationChanged(self, source_item):
        print("object location changed", self.display())
        #pass over the source files configuration
        self._previous_xml_data = source_item._previous_xml_data
        self._xml_data = source_item._xml_data
        self.object_relations = source_item.object_relations
        self._children = source_item._children
        
        
    def totalChildCount(self):
        total_childitems = self._children + self._filtered_children
        return len(total_childitems)

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                if not isinstance(task_object, _Element) and not isinstance(task_object, _Comment):
                    task_item = self.__class__(
                        application=self.application, 
                        object_class=task_object._xml_object_class, 
                        xml_custom_object=task_object, 
                        parent=self,
                        model_reference=self.model_reference)
                    self.addChild(task_item)

    def flags(self, column):
        return self.flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    @property
    def xml_object_class(self):
        return self._xml_data.xml_object_class

    @property
    def object_class(self):
        return self._object_class

    @object_class.setter
    def object_class(self, value):
        self._object_class = value

    @property
    def uid(self):
        if not self._uid:
            self._uid = str(uuid.uuid4())
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value

    def display(self):
        if self._xml_data:
            return self._xml_data.display
        return ""

    def setDisplay(self, value):
        if self._xml_data:
            self._xml_data.display = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def parent(self):
        return self._parent

    def setParent(self, parent):
        self._parent = parent

    def addChild(self, child, row=None):
        if row is not None and row <= self.childCount():
            # print('insert at', row)
            self._children.insert(row, child)
        else:
            # print('append to the end')
            self._children.append(child)
        self.itemAdded.emit(child)

    def removeChild(self, row):
        if row >= 0 and row <= len(self._children):
            return self._children.pop(row)

    def removeChildItem(self, childItem):
        if childItem in self._children:
            child_index = self._children.index(childItem)
            return self._children.pop(child_index)

    def removeItem(self):
        parent_item = self.parent()
        if not parent_item.removeChild(self.row()):
            parent_item.removeChildItem(self)
        if self._xml_data:
            self._xml_data.xml_delete_object()

    def child(self, row):
        if row >= 0 and row < len(self._children):
            return self._children[row]

    def childCount(self):
        return len(self._children)

    def row(self):
        if self.parent() and self in self.parent()._children:
            return self.parent()._children.index(self)
        else:
            if self in self.model_reference.rootItem._children:
                return self.model_reference.rootItem._children.index(self)
        return 0
    
    def setData(self, column, value):
        # print("set data", column, value)
        prev_value = self._xml_data.xml_get_attribute(column)
        if prev_value != value:
            # print(f"set item data for column with new value, {column}, previous value {prev_value}, new value {value}")
            self._xml_data.xml_set_attribute(column, value)
            self.data_changed.emit()
            self.columnValueChanged.emit(column, str(prev_value), str(value))
    
    def data(self, column, previous_state=False):
        if previous_state and self._previous_xml_data:
            return self._previous_xml_data.xml_get_attribute(column)

        if self._xml_data:
            return self._xml_data.xml_get_attribute(column)
            
        super().data(column)

    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

    def task_data(self):
        if self._xml_data is None:
            return self._xml_data
        export_data = {}
        export_data['xml_data'] = self._xml_data.string
        export_data['xml_object_class'] = self._xml_data.xml_object_class
        export_data['uid'] = self.uid
        export_data['objectclass'] = self.object_class
        export_data['row'] = self.row()
        return export_data

    @property
    def edit_data(self):
        return self.task_data()

    def update_data(self, dict_data):
        if self._previous_xml_data is None:
            # store the original data in case we want to restore it
            self._previous_xml_data = deepcopy(self.task_data())

        for key, value in dict_data.items():
            self.setData(key, value)

    def loadDataFromXML(self):
        # self.setText(0, self.display_name)
        if self._xml_data and self._xml_data.xml_object_class == "Transport_Object":
            self.object_relations = deepcopy(self._xml_data.xml_object_relations)
            self._xml_data.relations = self.object_relations

    def fromString(self, xml_string, xml_object_class):
        print("create xml node from string", xml_object_class)
        xml_node = fromstring(xml_string)
        parent_node = self.parent()._xml_data

        if xml_object_class == "Transport_Object":
            xml_object = object_container(parent=parent_node, source_element=xml_node)

        if xml_object_class == "Object_Transport_Task":
            xml_object = transport_task(parent=parent_node, source_element=xml_node, object_class="VI.Transport.ObjectTransport, VI.Transport")
        
        self._xml_data = xml_object
        children = xml_object.children()
        if children:
            self.loadChildren(children)
        
    def refreshModelStructure(self):
        parent_node = self.parent()._xml_data
        if parent_node:
            parent_node.xml_remove_children()
            siblings = self.parent()._children
            for xml_node in siblings:
                print("add node to hierarchy", xml_node._xml_data.display)
                parent_node.xml_append_node(xml_node._xml_data)


    def loadDatabaseObject(self):
        if self._xml_data is not None and self.application.db and self._xml_data.xml_object_class == "Transport_Object":
            table_name = self._xml_data.table_name
            self.object_data = self.application.db.get_db_object(table_name, self._xml_data.key_columns, "and" )
            print("Object Loaded", self.object_data is None)
            
            if len(self.object_data) > 0:
                self.object_data = self.object_data[0]
            
            db_relations = self.application.db.get_table_initial_relations(table_name)
            loaded_tables = [table_name]

            for xml_source_relation in self.object_relations:
                xml_table = xml_source_relation["ChildTable"]
                if xml_table not in loaded_tables:
                    loaded_tables.append(xml_table)
                    new_relations = self.application.db.get_table_initial_relations(xml_table)
                    db_relations = self.application.db.extend_table_relations(db_relations, new_relations)

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
            print("Object Relations Loaded", len(relations_sorted))

            """ save final relation data """
            self.object_relations = relations_sorted
            self._xml_data.relations = relations_sorted

    def listRelatedObjectData(self, override=False):
        if self._xml_data and self._xml_data.xml_object_class != "Transport_Object":
            return False

        if not self.application.db:
            return False
        
        self._children = []
        if self.object_data is None:
            self.loadDatabaseObject()

        data_dict = self.getRelatedObjectsData()
        if len(data_dict) > 0:
            self.model_reference.databaseObjectsLoaded.emit(self, data_dict)

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

    def getRelatedObjectsData(self):
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