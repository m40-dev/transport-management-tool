import uuid, re
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal, QTimer
from copy import deepcopy
from lxml.etree import _Element, _Comment, fromstring
from lib.ui.WidgetFactory import MsgBox

from .xml_object_definitions import *

FILTER_MIN_LEN = 1
LISTING_TIMER = 120

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
        self._object_relations = {}
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

        self.object_listing_timer = QTimer(self)
        self.object_listing_timer.setSingleShot(True)
        self.object_listing_timer.timeout.connect(self.listRelatedObjectData)

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
    
    def objectRelationsChanged(self):
        # print("relations changed")
        self.object_listing_timer.start(LISTING_TIMER)

    def resetRelationStates(self, state=0):
        # reset all relations
        if self._xml_data and self._xml_data.xml_object_class != "Transport_Object":
            return False

        for table, table_relations in self.object_relations.items():
            for relation_entry in table_relations:
                if state == 0:
                    # reset to 0 - unselected
                    relation_entry["Relation"] = 0
                if state == 1:
                    # reset to initial state
                    initial_state = relation_entry["InitialRelationState"]
                    relation_entry["Relation"] = initial_state
        # remap the object relations with setter
        self.object_relations = self.object_relations
        # refresh object listing
        self.objectRelationsChanged()

    @property
    def object_relations(self):
        relation_data = self._object_relations
        # compatibility with the old relations handling structure
        if isinstance(relation_data, list):
            parsed_relations = {}
            for relation in relation_data:
                table_name = relation.get("ChildTable", None)
                if table_name not in parsed_relations.keys():
                    parsed_relations[table_name] = [relation]
                else:
                    parsed_relations[table_name].append(relation)
            self._object_relations = parsed_relations
        return self._object_relations
        
    @object_relations.setter
    def object_relations(self, relations_data):
        self._object_relations = relations_data
        if self._xml_data and isinstance(self._xml_data, transport_template_custom_object):
            self._xml_data.xml_object_relations = relations_data
        self.objectRelationsChanged()

    def itemDataDropped(self, source_dict):
        print("foreign model object dropped", source_dict.get("objectclass", None))
        source_dict.get("object_data", {})
        object_info = source_dict.get("object_info", None)

        parent_xml_node = self.parent()._xml_data
        if parent_xml_node:
            object_xml_node = parent_xml_node.xml_add_child_node(object_info)
            self._xml_data = object_xml_node
        # load initial object relations
        if not object_info:
            return
        
        table_name = object_info.get("table_name", None)
        if table_name:
            object_relations = self.application.db.get_table_initial_relations(table_name=table_name, extended_view=True)
            self.object_relations = object_relations
            # self._xml_data.xml_object_relations = self.object_relations
            self.resetRelationStates(0)

    def itemLocationChanged(self, source_item):
        print("object location changed", self.display(0
        ), source_item)
        #pass over the source files configuration
        if not isinstance(source_item, XMLDataItem):
            return False

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

    @property
    def xml_object_class(self):
        if self._xml_data and isinstance(self._xml_data, transport_template_custom_object):
            return self._xml_data.xml_object_class
        return None

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

    def display(self, column):
        if self._xml_data:
            if isinstance(self._xml_data, transport_template_custom_object) and column == "XML Transport Structure":
                return self._xml_data.display
            
            if isinstance(self._xml_data, transport_template_custom_object) and column == "Options":
                return self._xml_data.option

        return self.data(column)

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
        if row >= 0 and row <= len(self._children) and len(self._children) > 0:
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
        return True
    
    def isCheckable(self, column_name):
        if self._xml_data and isinstance(self._xml_data, transport_template_custom_object):
            if column_name == "Options":
                if len(self._xml_data.option.strip()) > 0:
                    return True
        return False


    def checkState(self, column_name):
        # print("get check state for column", column_name, self.Relation)
        if self._xml_data and isinstance(self._xml_data, transport_template_custom_object):
            if column_name == "Options":
                return self._xml_data.state
        return 0

    def setCheckState(self, column_name, value):
        # print("set check state for column", column_name, value)
        if self._xml_data and isinstance(self._xml_data, transport_template_custom_object):
            self._xml_data.state = value
        return True

    def data(self, column, previous_state=False):
        if previous_state and self._previous_xml_data:
            return self._previous_xml_data.xml_get_attribute(column)

        if self._xml_data:
            return self._xml_data.xml_get_attribute(column)
            

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
            # self._xml_data.relations = self.object_relations
        if self.application.autoLoadDatabaseObjects():
            self.loadDatabaseObject()

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
                # print("add node to hierarchy", xml_node)
                parent_node.xml_append_node(xml_node._xml_data)

    def loadDatabaseObject(self):
        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()
        
        if self._xml_data is not None and self._xml_data.xml_object_class == "Transport_Object":
            table_name = self._xml_data.table_name
            self.object_data = self.application.db.get_db_object(table_name, self._xml_data.key_columns, " and " )
            
            if len(self.object_data) > 0:
                self.object_data = self.object_data[0]
            
            db_relations = self.application.db.get_table_initial_relations(table_name, extended_view=True)

            for xml_source_table in self.object_relations.keys():
                if xml_source_table not in db_relations.keys():
                    new_relations = self.application.db.get_table_initial_relations(xml_source_table)
                    db_relations[xml_source_table] = new_relations

            if db_relations is not None:
                for db_relation_items in db_relations.values():
                    for db_relation in db_relation_items:
                        db_relation["Relation"] = 0
            
            """ select all base relations that match the xml relation state, skip relations that are not marked for transport in the database """
            selected_relations, skipped_relations = self.select_referenced_relations(source=self.object_relations, target=db_relations)

            """ select leftover relations where we can match the parent column with the child column """
            selected_relations, skipped_relations = self.select_skipped_relations(skipped_relations, selected_relations, db_relations, match_parent_column=True)
            
            # """ select leftover relations where the xml relation matches and do not try to match the parent column anymore (basically include all relations where necessary) """
            # selected_relations, skipped_relations = self.select_skipped_relations(skipped_relations, selected_relations, db_relations, match_parent_column=False)
    
            relations_sorted = dict(sorted(db_relations.items()))
            print("Object Relations Loaded", len(relations_sorted))

            """ save final relation data """
            self.object_relations = relations_sorted
            # self._xml_data.relations = relations_sorted

    def listRelatedObjectData(self, override=False):
        if self._xml_data and self._xml_data.xml_object_class != "Transport_Object":
            return False

        if not self.application.autoListDatabaseObjects() and not override:
            return False

        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()

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
                    
        return self.select_referenced_relations(source={"FollowUp": follow_up_relations}, target=target, ignore_initial_state=True, match_parent_column=match_parent_column)

    def select_referenced_relations(self, source, target, ignore_initial_state=False, match_parent_column=True):
        skipped_relations = {}
        selected_relations = {}

        # Source items are the ones that were defined in the XML file 
        for source_table, xml_source_relations in source.items():
            for xml_source_relation in xml_source_relations:
                xml_table = xml_source_relation["ChildTable"]
                xml_column = xml_source_relation["ChildColumn"]
                xml_relation = xml_source_relation["Relation"]

                # Target items are the loaded database relations
                for target_table, target_relations in target.items():
                    for db_relation in target_relations:
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
            for source_table, relations in self.object_relations.items():
                for relation in relations:
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
            for relations in self.object_relations.values():
                for relation in relations:
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
        
        if self.application.db and not self.application.db.is_connected:
            return self.application.databaseConnectionRequired()

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

    @property
    def script(self):
        if self._xml_data:
            return self._xml_data.text
        return ""
    
    @script.setter
    def script(self, script_value):
        if self._xml_data and self.xml_object_class == "Transport_SQL_Object":
            byte_data = bytes(script_value, 'utf-8')
            byte_data = byte_data.replace(b'\r\n', b'\n')
            self._xml_data.text = byte_data.decode('utf-8')