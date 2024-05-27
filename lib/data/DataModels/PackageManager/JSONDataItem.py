import uuid
from PyQt6.QtCore import Qt, pyqtSignal, QObject, pyqtSignal
from copy import deepcopy
import re, os
from pathlib import Path

FILTER_MIN_LEN = 1

class JSONDataItem(QObject):
    data_changed = pyqtSignal()
    locationChanged = pyqtSignal(object) 
    dataDropped = pyqtSignal(dict)
    itemAdded = pyqtSignal(object)
    columnValueChanged = pyqtSignal(str, str, str)

    def __init__(self, application, task_class="JSONDataItem", task_data=None, parent=None, model_reference=None):
        super().__init__(parent=parent)
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration
        self.model_reference = model_reference
        self._task_class = task_class
        self._parent = parent
        self._children = []
        self._filtered_children = []
        self._task_data = task_data
        self._previous_task_data = None
        self._uid = str(uuid.uuid4())
        self._is_saved = True
        self._filter_match = True
        self.filter_string = ""
        self.item_class_configuration = self.application.getConfigurationParameters(self.task_class)
        self.source_files = None
        self.source_files_text = None
        self.useExperimentalFeatures = self.ProgramConfiguration.getConfigurationValue("ObjectModel", "UseExperimental")
        
        if model_reference:
            model_reference.filterStringChanged.connect(self.handleFilterStringChanged)
        
        if task_data:
            self.initialize_data()
            children = task_data.get("children", None)
            if children:
                self.loadChildren(children)

        if self.task_class and self.useExperimentalFeatures:
            self.configureSourceColumns(dynamic_only=True)

        self.dataDropped.connect(self.itemDataDropped)
        self.locationChanged.connect(self.itemLocationChanged)
        self.locationChanged.connect(self.updateSortOrder)

    def configureSourceColumns(self, parent_only=False, dynamic_only=False):
        source_map_columns = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_setting(self.task_class, "ValuePattern")
        for column, column_configuration in source_map_columns.items():
            source_mapping = column_configuration.get("ValuePattern", None)
            if source_mapping and parent_only and "PARENT." not in source_mapping.upper():
                #Skip non-parent relations
                continue
            isForExport = column_configuration.get("IsForDataExport", True)
            if source_mapping and dynamic_only and isForExport:
                #Skip standard, exportable columns, calculate only the dynamically calculated fields
                continue

            source_value = self.parseStringPattern(source_mapping)
            if source_value:
                self.setData(column, source_value)
        
        #recursively apply to child items
        total_childitems = self._children + self._filtered_children
        if len(total_childitems) > 0:
            for child_item in total_childitems:
                child_item.configureSourceColumns()

    def parseStringPattern(self, string_pattern):
        regex_pattern = r'%([^%]+)%'
        matches = re.findall(regex_pattern, string_pattern)
        replacement_dict = {}
        
        for column_pattern in matches:
            column_name = column_pattern
            substring_chars = 0
            if ":" in column_pattern:
                #try to substring the value
                column_name, substring_chars = column_pattern.split(":")
                if substring_chars.isnumeric():
                    substring_chars = int(substring_chars)
            
            if column_pattern not in replacement_dict.keys():
                column_value = self.getSourceValue(column_name)
                replacement_dict[column_pattern] = column_value
            
            if substring_chars > 0 and column_pattern in replacement_dict.keys() :
                replacement_dict[column_pattern] = replacement_dict[column_pattern][:substring_chars]
            
        # replacement_dict = self.get_replacement_values(matches, previous_state)
        parsed_string = re.sub(regex_pattern, lambda match: replacement_dict.get(match.group(1), match.group(0)), string_pattern)
        return parsed_string

    def getSourceValue(self, source_mapping):
        if "." in source_mapping:
            source = source_mapping.split(".")[0]
            source_column = source_mapping.split(".")[1:]
            if len(source_column) > 0:
                # more than one level higher, pass this to the source
                source_column = ".".join(source_column)
            if source.upper() == "PARENT" and self.parent():
                return self.parent().getSourceValue(source_column)
            
            return self.task_data().get(source_column, "")
        return self.task_data().get(source_mapping, "")

    def itemDataDropped(self, source_dict):
        # print("foreign model object dropped", source_dict.get("objectclass", None), self.task_class)
        pass

    def itemLocationChanged(self, source_item):
        # print("object location changed", self.display)
        #pass over the source files configuration
        self._previous_task_data = source_item._previous_task_data
        self.source_files = source_item.source_files
        self.source_files_text = source_item.source_files_text
        self.configureSourceColumns(parent_only=True)
        
    @property
    def filter_match(self):
        return self._filter_match

    @filter_match.setter
    def filter_match(self, value):
        self._filter_match = value
        if value and self.parent():
            self.parent().filter_match = True

    def handleFilterStringChanged(self, filter_string):
        filter_match = self.check_filter_conditions(filter_string)
        self.filter_match = filter_match

    def filter_childCount(self):
        return len(self.filter_childItems())

    def totalChildCount(self):
        total_childitems = self._children + self._filtered_children
        return len(total_childitems)

    def filter_childItems(self):
        # Iterate over child items, if any of them is matching the filter criterias
        # add child item to temporary list and reset the children list
        filter_rows = []
        hidden_rows = []
        all_items = self._children + self._filtered_children
        for data_item in all_items:
            if data_item.filter_match:
                filter_rows.append(data_item)
            else:
                hidden_rows.append(data_item)

        #temporary assign filtered rows as item children
        sorted_filter_rows = sorted(filter_rows, key=lambda item: item.sortOrder)
        # for item in sorted_filter_rows:
        #     print(f"sorted {item.display}")

        self._children = sorted_filter_rows
        self._filtered_children = hidden_rows

        #return filtered rows
        return sorted_filter_rows, hidden_rows
    
    @property
    def sortOrder(self):
        treeview_order = self.row()
        if self.item_class_configuration:
            sort_column_configuration = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_role(self.task_class, "SortOrder")
            if len(sort_column_configuration) == 0:
                return str(treeview_order)
            sort_column = list(sort_column_configuration.keys())[0]
            sort_order = self.data(sort_column)
            if sort_order:
                treeview_order = sort_order
        return str(treeview_order)

    def updateSortOrder(self, validate_siblings=True):
        # print("update sort order")
        treeview_order = self.row()
        sort_column_configuration = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_role(self.task_class, "SortOrder")
        if len(sort_column_configuration) == 0:
            return treeview_order
        
        sort_column = list(sort_column_configuration.keys())[0]
        sort_column_configuration = list(sort_column_configuration.values())[0]
        
        if sort_column_configuration:
            min_value = sort_column_configuration.get("MinValue", 1)

            if treeview_order == 0:
                treeview_order = min_value
                if treeview_order != self.data(sort_column):
                    self.setData(sort_column, treeview_order)
                return treeview_order

            max_value = sort_column_configuration.get("MaxValue", 999)
            sibling_count = self.parent().childCount()

            if sibling_count <= 0:
                sibling_count = 1
            if treeview_order >= sibling_count-1:
                treeview_order = max_value
                if treeview_order != self.data(sort_column):
                    self.setData(sort_column, treeview_order)
                return treeview_order

            value_range = (max_value - min_value)

            treeview_order = treeview_order + min_value
                            
            if sort_column_configuration.get("DistributeEvenly", False) == True:
                sorting_step = value_range / sibling_count
                treeview_order = round(sorting_step * treeview_order )
            
            if validate_siblings:
                sibling_above = self.parent().child(self.row()-1)
                sibling_below = self.parent().child(self.row()+1)
                
                if sibling_above and sibling_below:
                    gap = int(sibling_below.sortOrder) - int(sibling_above.sortOrder) 
                    treeview_order = round(gap / 2) + int(sibling_above.sortOrder)
                else:
                    #just one sibling around, stick to the range
                    if sibling_above and int(sibling_above.sortOrder) >= treeview_order:
                        treeview_order = max_value
                    
                    if sibling_below and int(sibling_below.sortOrder) <= treeview_order:
                        treeview_order = min_value
        
        if treeview_order <= min_value:
            treeview_order = min_value

        if treeview_order >= max_value:
            treeview_order = max_value

        if treeview_order != self.data(sort_column):
            self.setData(sort_column, treeview_order)
        return treeview_order


    def check_filter_conditions(self, filter_string):
        #Initially set filter to true (show all items) if no filter is provided
        self.filter_string = filter_string
        if not filter_string or len(filter_string.strip()) <= FILTER_MIN_LEN:
            return True
        
        filter_configuration = self.parse_filter(filter_string)

        #initially turn off visibility, this flag will be switched during validation
        item_match = False

        #criteria matching starts at 0, every filter criteria that matches for the item will increase this number by 1 
        criteria_match = 0

        #General freetext display/description match condition
        if "freetext" in filter_configuration.keys():
            filter_values = filter_configuration.get("freetext", [])
            #since filter text can have multiple values, check each of them separately
            for filter_text in filter_values:
                #simple display name and description comparison
                value_check = (filter_text.lower() in self.display.lower() 
                                or filter_text.lower() in self.description.lower())
                #if any of the entries matches, mark the result and exit the loop
                if value_check:
                    criteria_match += 1
                    break

        #check object properties according to the object configuration
        if self.item_class_configuration:
            for object_data_column in self.item_class_configuration.keys():
                
                #filter values if  object configuration column is detected in the filter
                if object_data_column.lower() in filter_configuration.keys():
                    
                    #filter configuration always returns column names in lower case
                    filter_values = filter_configuration.get(object_data_column.lower(), [])

                    #filtered attribuets might have multiple values provided, each value is checked separately
                    for filter_text in filter_values:

                        # validating only if the filter text is provided
                        if len(filter_text) > 0:

                            #read current object value
                            object_value = self._task_data.get(object_data_column, None)

                            #continue filtering only if we have the object value (is not None)
                            if object_value is not None:

                                #in case of lists, concatenate values for comparison
                                if isinstance(object_value, list):
                                    object_value = ",".join(object_value)

                                #simple string comparison
                                value_check = str(filter_text).lower() in str(object_value).lower()
                                if value_check:
                                    #mark the criteria and break the ineration over the filter values, at least one entry matches
                                    criteria_match += 1
                                    break
        # if the criteria match is equal to the number of provided filters, it is considered as match
        if criteria_match == len(filter_configuration.keys()):
            item_match = True
        
        #Return final verification state
        return item_match 

    def parse_filter(self, filter_string):
        #Create empty filter configuration
        filter_configuration = {}
        #Split the initial filter conditions
        conditions = filter_string.split(";")

        #iterate over defined conditions
        for condition in conditions:
            #ignore empty spaces in the condition element
            if len(condition.strip()) == 0:
                continue
            
            #define the filter column as freetext initially
            column = "freetext"
            values_list = [condition.strip()]
            
            #check for the column condition markers, colon marks the column: value pairs in the filter
            if ":" in condition:
                column, values = condition.split(":")[:2]
                #initially put the values into a new list
                values_list = [values]
                #check for the value separation markers. values divided by comma will be evaluated separately
                if "," in values:
                    values_list = values.split(",")
            else:
                #if we do not have the column marker, but freetext is separated with comma, treat them as separate values 
                if "," in condition:
                    values_list = condition.split(",")
            
            #make the column lower case for easier comparison later on, also remove whitespaces from column and values
            column = column.lower().strip()
            values_list = list(map(str.strip, values_list))
            if column not in filter_configuration.keys():
                #remove whitespaces from the values and save them in the freetext filter 
                filter_configuration[column] = values_list
            else:
                filter_configuration[column] = filter_configuration[column] + values_list
        return filter_configuration

    def loadChildren(self, child_tasks):
        if child_tasks:
            for task_object in child_tasks:
                task_class = task_object.get("objectclass", None)
                task_item = self.__class__(
                    application=self.application, 
                    task_class=task_class, 
                    task_data=task_object, 
                    parent=self,
                    model_reference=self.model_reference)
                self.addChild(task_item)

    def flags(self, column):
        return self.flags | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable

    @property
    def task_class(self):
        return self._task_class

    @task_class.setter
    def task_class(self, value):
        self._task_class = value
        self.item_class_configuration = self.application.getConfigurationParameters(value)

    @property
    def uid(self):
        if not self._task_data.get("uid", None) and not self._uid:
            self._uid = str(uuid.uuid4())
        return self._uid

    @uid.setter
    def uid(self, value):
        self._uid = value
        self._task_data["uid"] = value

    @property
    def display(self):
        configuration = self.item_class_configuration
        
        if configuration is None:
            return ""
        display_text = []
        for field, field_configuration in configuration.items():
            is_display_column = "DisplayRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            text = str(self._task_data.get(field, ""))
            if len(text.strip()) > 0:
                display_text.append(text.strip())
        if len(display_text) > 0:
            return ", ".join(display_text)
        return ""
    
    @display.setter
    def display(self, value):
        configuration = self.item_class_configuration
        
        if configuration is None:
            return ""
        
        for field, field_configuration in configuration.items():
            is_display_column = "DisplayRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            self.setData(field, value)
            return True

    @property
    def description(self):
        configuration = self.item_class_configuration
        
        if configuration is None:
            return ""
        display_text = []
        for field, field_configuration in configuration.items():
            is_display_column = "DescriptionRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            text = str(self._task_data.get(field, ""))
            if len(text.strip()) > 0:
                display_text.append(text.strip())
        if len(display_text) > 0:
            return ", ".join(display_text)
        return ""

    @description.setter
    def description(self, value):
        configuration = self.item_class_configuration
        
        if configuration is None:
            return ""
        
        for field, field_configuration in configuration.items():
            is_display_column = "DescriptionRole" in field_configuration.get("FieldRole", [])
            if not is_display_column:
                continue
            self.setData(field, value)
            return True

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
        parent_item.removeChild(self.row())

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
        if not self._task_data:
            return False
            
        prev_value = self._task_data.get(column, "")
        if prev_value != value:
            # set new value
            self._task_data[column] = value
            
            # get current column configuration
            column_config = self.item_class_configuration.get(column, None)

            # mark item as changed / styling, saving
            if column_config and column_config.get("IsForDataExport", True):
                #update 'saved' state only if the changed column is exportable
                self.is_saved = False

            #emit data change signals
            self.data_changed.emit()
            self.columnValueChanged.emit(column, str(prev_value), str(value))
    
    def data(self, column, previous_state=False):
        if previous_state and self._previous_task_data:
            return self._previous_task_data.get(column,  None)

        if self._task_data:
            return self._task_data.get(column,  None)
            
        return None

    def insertChildren(self, row, child_objects):
        if row == -1:
            row = 0
        
        for element in child_objects:
            # print("add child", element.display)
            self.addChild(element, row)
            row +=1

    @property
    def is_saved(self):
        return self._is_saved
    
    @is_saved.setter
    def is_saved(self, state):
        self._is_saved = state
        if state is False and self.parent():
            self.parent().is_saved = state
            self.parent().data_changed.emit()

    def save(self):
        self._previous_task_data = None
        self.is_saved = True
        self.data_changed.emit()
        
        for child_node in self._children:
            child_node.save()

    def get_children_data(self, task_class=None, export_data=False):
        children = []
        if self.childCount() == 0:
            return children

        for child_item in self._children:
            if export_data:
                child_data = child_item.export_data()
            else:
                child_data = child_item.task_data()
            
            if task_class and child_item.task_class == task_class:
                children.append(child_data)
                continue
            
            if task_class is None:
                children.append(child_data)
        return children

    def task_data(self):
        if self._task_data is None:
            return self._task_data

        export_data = deepcopy(self._task_data)
        # export_data = self._task_data
        export_data['uid'] = self.uid
        export_data['objectclass'] = self.task_class
        export_data['row'] = self.row()
        export_data['children'] = self.get_children_data()
        export_data['source_file_data'] = self.source_files_text
        return export_data

    def get_parent_data(self):
        if not self.parent():
            return None

        parent = self.parent()
        if parent._task_data is None or parent.task_class=="RootItem":
            return {}
        
        object_data = deepcopy(parent._task_data)
        # object_data = parent._task_data
        object_data['uid'] = parent.uid
        object_data['objectclass'] = parent.task_class
        object_data['row'] = parent.row()
        if "children" in object_data:
            object_data.pop("children")

        return object_data

    @property
    def edit_data(self):
        return self.task_data()

    def update_data(self, dict_data):
        if self._previous_task_data is None:
            # store the original data in case we want to restore it
            self._previous_task_data = deepcopy(self.task_data())

        for key, value in dict_data.items():
            self.setData(key, value)

    def initialize_data(self):
        configuration = self.item_class_configuration
        if self._task_data is None or configuration is None:
            return False

        object_data = self.task_data()

        for field, field_configuration in configuration.items():
            is_for_export = field_configuration.get("IsForDataExport", True) == True
            if not is_for_export:
                continue

            object_field_value = object_data.get(field, "")
            field_role = field_configuration.get("FieldRole", None)
            
            if field_role and field_role == "SortOrder":
                #set sort order
                self._task_data[field] = int(self.sortOrder)
                continue

            if field_role and field_role == "UniqueIdentifier" and len(object_field_value) == 0:
                # generate UIDs
                self._task_data[field] = str(uuid.uuid4())
                continue

    def clone_task_data(self):
        if self._task_data is None:
            return {}
        export_data = {}
        
        configuration = self.item_class_configuration
        object_data = self.task_data()

        if configuration is None:
            return object_data

        for field, field_configuration in configuration.items():

            object_field_value = object_data.get(field, "")

            field_type = field_configuration.get("FieldType", None)
            field_role = field_configuration.get("FieldRole", None)

            if field_role and field_role == "UniqueIdentifier":
                # do not clone UID fields
                export_data[field] = str(uuid.uuid4())
                continue

            if field_role and field_role == "DisplayRole":
                # mark display columns with prefix
                export_data[field] = "[CLONE] " + object_field_value
                continue


            export_data[field] = object_field_value
        return export_data


    def export_data(self):
        if self._task_data is None:
            return self._task_data
        
        configuration = self.item_class_configuration
        
        export_data = {}
        object_data = self.task_data()

        exportBooleanAsString = self.ProgramConfiguration.getConfigurationValue("Package Manager", "ExportBooleanAsString")
        exportIntegerAsString = self.ProgramConfiguration.getConfigurationValue("Package Manager", "ExportIntegerAsString")
        
        if configuration is None:
            return object_data

        for field, field_configuration in configuration.items():
            is_for_export = field_configuration.get("IsForDataExport", True) == True
            if not is_for_export:
                continue
            object_field_value = object_data.get(field, "")
            export_data[field] = object_field_value

            field_type = field_configuration.get("FieldType", None)
            field_role = field_configuration.get("FieldRole", None)
            
            if field_role and field_role == "SortOrder":
                #set sort order
                export_value = int(self.sortOrder)
                if exportIntegerAsString:
                    export_value = str(export_value)
                export_data[field] = export_value
                continue

            if field_role and field_role == "UniqueIdentifier" and len(object_field_value) == 0:
                object_field_value = str(uuid.uuid4())
                export_data[field] = str(object_field_value)
                continue

            if field_type and field_type == "ChildObjectReference":
                child_class = field_configuration.get("Class", None)
                export_data[field] = self.get_children_data(task_class=child_class, export_data=True)
                continue

            if field_type and field_type == "ListInput":
                object_value = self._task_data.get(field, [])
                
                if isinstance(object_value, list) and len(object_value) > 0:
                    values = 0
                    for entry in object_value:
                        if len(str(entry).strip()) > 0:
                            values += 1
                            break
                    if values == 0:
                        object_value = []

                export_data[field] = object_value
                if not isinstance(object_value, list):
                    export_data[field] = [str(object_value)]
                    self._task_data[field] = [str(object_value)]
                continue
            
            if field_type and field_type == "BooleanInput":

                object_field_value = str(object_field_value).strip()
                if len(object_field_value) == 0:
                    object_field_value = "False"
                
                object_field_value = object_field_value.upper() == "TRUE"

                if exportBooleanAsString:
                    object_field_value = str(object_field_value)

                export_data[field] = object_field_value
                continue
            
            if field_type and field_type == "IntegerInput":
                #set sort order
                export_value = str(object_field_value)
                if export_value.isnumeric():
                    export_value = int(export_value)
                else:
                    export_value = field_configuration.get("DefaultValue", 0)

                if exportIntegerAsString:
                    export_value = str(export_value)

                export_data[field] = export_value
                continue

        return export_data

    def get_file_data(self, reload_data=False):
        # get the object_uid: file_path pairs from item
        if self.source_files and not reload_data:
            return self.source_files

        file_configurations = {}
        column_configurations = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_type(self.task_class, "FileInput")
        for column in column_configurations:
            file_path = self.get_file_path(file_column=column)
            file_configurations[column] = file_path
        return file_configurations
    
    def get_file_strings(self, reload_data=False):
        # get the object_uid: file_path pairs from item
        if self.source_files_text and not reload_data:
            return self.source_files_text

        file_configurations = {}
        column_configurations = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_type(self.task_class, "FileInput")
        for column in column_configurations:
            file_path = self.get_file_path(file_column=column)
            if file_path:
                relative_location = file_path.relative_to(self.application.current_workdir)
                file_configurations[column] = str(relative_location)
        return file_configurations

    def get_all_files(self, recursive=False):
        file_configurations = list(self.get_file_data().values())
        if recursive and self.childCount() > 0:
            for child_item in self._children:
                child_configuration = child_item.get_all_files(recursive)
                if len(child_configuration) > 0:
                    file_configurations = file_configurations + child_configuration
        return file_configurations

    def update_file_locations(self):  
        # print("update file locations", self.display, self.source_files)    
        column_configurations = self.ProgramConfiguration.ObjectModel.get_columns_configuration_by_type(self.task_class, "FileInput")
        if column_configurations and self.source_files:
            for column in column_configurations.keys():
                source_file = self.source_files.get(column, None)
                target_file = self.get_file_path(file_column=column)
                if source_file and target_file and Path(source_file) != Path(target_file):
                    self.moveFile(source_file, target_file)
        self.source_files = self.get_file_data(reload_data=True)
        self.source_files_text = self.get_file_strings(reload_data=True)


    def get_file_path(self, file_location=None, file_column="DefinitionFile", previous_state=False):
        if not file_location:
            file_location = self.data(file_column, previous_state)
        
        if not file_location:
            return file_location

        object_configuration = self.item_class_configuration
        if object_configuration:
            definition_file_configuration = object_configuration.get(file_column, None)
            if definition_file_configuration:
                if definition_file_configuration.get("FileSelectionMode", "") == "Relative":
                    file_path = Path(os.sep.join([self.application.current_workdir, file_location]))
                    return file_path

                if definition_file_configuration.get("FileSelectionMode", "") == "Absolute":
                    file_path = Path(file_location)
                    return file_path

                if definition_file_configuration.get("FileSelectionMode", "") == "FileName":
                    parent_directory_path = self.application.current_workdir
                    file_path = Path(os.sep.join([parent_directory_path, file_location]))
                    
                    redirection_relative_to = definition_file_configuration.get("RedirectDirectoryRelativeTo", None)
                    if redirection_relative_to and redirection_relative_to.lower() == "parent" and self.parent():
                        # target directory should be relative to parent object, not to workdir
                        parent_location = self.parent().data(file_column, previous_state)
                        if previous_state and self.parent()._previous_task_data:
                            #previous data state is required, but parent location is determined by the DefinitionFile path
                            parent_location = self.parent()._previous_task_data.get("DefinitionFile")

                        parent_file_path = self.parent().get_file_path(parent_location, previous_state=previous_state)
                        
                        if parent_file_path:
                            parent_directory_path = Path(parent_file_path).parent
                        
                        # print(f"get file path in previous state {previous_state}, parent location {parent_directory_path}")

                    static_redirect = definition_file_configuration.get("RedirectDirectoryStatic", None)
                    if static_redirect:
                        # Redirect File To different Directory
                        file_path = Path(os.sep.join([str(parent_directory_path), str(static_redirect), file_location]))
                        return file_path
                    
                    dynamic_redirect = definition_file_configuration.get("RedirectDirectoryDynamic", None)
                    if dynamic_redirect:
                        # Redirect File To different Directory based on the object parameters
                        dynamic_redirect = self.parse_text_pattern(dynamic_redirect, previous_state)
                        file_path = Path(os.sep.join([str(parent_directory_path), str(dynamic_redirect), file_location]))
                        # print("dynamic file location", file_path)
                        return file_path
                    return file_path
        return file_location

    def get_replacement_values(self, replacement_columns, previous_state=False):
        replacement_dict = {}
        for column in replacement_columns:
            column_value = self.task_data().get(column, "")
            if previous_state and self._previous_task_data:
                column_value = self._previous_task_data.get(column, "")

            if "parent." in column.lower() and self.parent():
                # parent object reference
                parent_column = column.split(".")[1]
                column_value = self.parent().task_data().get(parent_column, "")
                if previous_state and self.parent()._previous_task_data:
                    column_value = self.parent()._previous_task_data.get(parent_column, "")
            replacement_dict[column] = column_value
        return replacement_dict

    def parse_text_pattern(self, string_pattern, previous_state=False):
        regex_pattern = r'%([^%]+)%'
        matches = re.findall(regex_pattern, string_pattern)
        replacement_dict = self.get_replacement_values(matches, previous_state)
        parsed_string = re.sub(regex_pattern, lambda match: replacement_dict.get(match.group(1), match.group(0)), string_pattern)
        return parsed_string

    def moveFile(self, source_path, destination_path):
        # print(f"moving {source_path} to {destination_path}")
        if not source_path or not destination_path:
            return False

        if not source_path.is_file():
            # source file not found
            # print("source file not found:", source_path)
            return False

        destination_path.parent.mkdir(parents=True, exist_ok=True)
        destination_path = source_path.replace(destination_path)
        self.application.PackageManager.deleteDirectory(source_path.parent)

    @property
    def is_transport(self):
        is_transport = False
        task_type = self._task_data.get("TaskType", None)
        
        if not task_type:
            return is_transport 

        task_type_configuration = self.item_class_configuration.get("TaskType", None)
        if task_type_configuration:
            template_configuration = task_type_configuration.get("XMLTemplateTypes", None)
            if template_configuration:
                is_transport = task_type in template_configuration
        
        return is_transport