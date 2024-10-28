from lxml import etree
from lib.data.DataModels.XMTemplateEditor.xml_object_definitions.transport_template_custom_object import transport_template_custom_object
from lib.data.DataModels.XMTemplateEditor.xml_object_definitions.object_parameter import object_parameter
            

class object_container(transport_template_custom_object):
    def __init__(self, parent, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations={}):
        super(object_container, self).__init__(parent=parent, node_class="Parameter", source_element=source_element)
        
        self._object_relations = relations
        self.pk_columns = pk_columns
        self.base_object_node = None
        self.delete_residuals_node = None
        self.object_relations_node = None

        """ Main Container Node setup"""
        if source_element is None:
            self.data.attrib['Name'] = "Container"

            """ Container transport settings """
            self.delete_residuals_node = object_parameter(self, "DeleteResiduals", delete_residual_objects)

            """ Add selected Transport relations """
            self.object_relations_node = object_parameter(self, "Relations")

            self.base_object_node = object_parameter(self, "BaseObject")

            base_object_table = object_parameter(self, "Tablename", base_table)
            base_object_display = object_parameter(self, "Display", display_name)
            
            """ build the object container """
            self.base_object_node.xml_append_node(base_object_table)
            self.base_object_node.xml_append_node(base_object_display)

            base_object_columns = object_parameter(self, "Columns")
            for pk_column, pk_column_value in pk_columns.items():
                if pk_column is not None:
                    base_object_column = object_parameter(self, pk_column, pk_column_value)
                    base_object_columns.xml_append_node(base_object_column)

            self.base_object_node.xml_append_node(base_object_columns)

            """ attach container to the xml structure"""
            self.xml_append_node(self.base_object_node)
            self.xml_append_node(self.delete_residuals_node)
            self.xml_append_node(self.object_relations_node)

            self.reset_container_relations()

        else:
            """ load data from source element """
            for element in self.children():
                if element.attrib["Name"] == "BaseObject":
                    self.base_object_node = object_parameter(self, "BaseObject", source_element=element)
                    # print(element)
                    
                if element.attrib["Name"] == "DeleteResiduals":
                    self.delete_residuals_node = object_parameter(self, "DeleteResiduals", source_element=element)
                if element.attrib["Name"] == "Relations":
                    self.object_relations_node = object_parameter(self, "Relations", source_element=element)
    
    @property
    def xml_object_class(self):
        return "Transport_Object"

    @property
    def accepted_classes(self):
        # define what class is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all objects 
        return ["Transport_Object", "ObjectDataItem"]

    @property
    def accepted_tables(self):
        # define what table is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all tables 
        return []

    @property
    def option(self):
        return "Delete Residual Items"

    @property
    def state(self):
        value = self.delete_residuals 
        if value > 0:
            value = 2
        return value
    
    @state.setter
    def state(self, value):
        if value > 0:
            value = 1
        self.set_delete_residuals(value)

    @property
    def description(self):
        container_description = etree.Comment(self.display)
        return container_description
    
    @property
    def table_name(self):
        table_name = ""
        if isinstance(self.base_object_node, transport_template_custom_object):
            for base_object_data_node in self.base_object_node.xml_get_children():
                if base_object_data_node.attrib["Name"] == "Tablename":
                    return base_object_data_node.text
        return table_name
    
    @property
    def key_columns(self):
        key_columns = {}
        if isinstance(self.base_object_node, transport_template_custom_object):
            for base_object_data_node in self.base_object_node.xml_get_children():
                if base_object_data_node.attrib["Name"] == "Columns":
                    for column_node in base_object_data_node.getchildren():
                        column_name = column_node.attrib.get("Name", "")
                        column_value = column_node.text
                        key_columns[column_name] = column_value
        return key_columns

    @property
    def display(self):
        display_name = ""
        if isinstance(self.base_object_node, transport_template_custom_object):
            for base_object_data_node in self.base_object_node.children():
                if base_object_data_node.attrib["Name"] == "Display":
                    return base_object_data_node.text
        return display_name

    @display.setter
    def display(self, value):
        if isinstance(self.base_object_node, transport_template_custom_object):
            for base_object_data_node in self.base_object_node.children():
                if base_object_data_node.attrib["Name"] == "Display":
                    base_object_data_node.text = value
                    return
        self.xml_set_attribute("Display", value)
            
    @property
    def xml_object_relations(self):
        object_relations = {}

        if isinstance(self.object_relations_node, transport_template_custom_object):
            for relation in self.object_relations_node.xml_get_children():
                relation_data = []
                if "|" in relation.text:
                    relation_data = relation.text.split("|")
                
                if len(relation_data) != 3:
                    # print("skip entry", relation.text)
                    continue

                child_table = relation_data[0]
                child_column = relation_data[1]
                relation_state = relation_data[2]
                relation_number = 0

                if "IgnoreInSupersetHandling" in relation_state:
                    relation_number = 4
                if "CR" in relation_state:
                    relation_number += 2
                if "FK" in relation_state:
                    relation_number += 1
                if "BOTH" in relation_state.upper():
                    relation_number += 3
                
                relation_entry = {
                        "Caption": f"{child_table} - > {child_column}",
                        "ParentTable": "", 
                        "ParentColumn": "", 
                        "Relation": relation_number,
                        "ChildTable": child_table,
                        "ChildColumn": child_column,
                        "InitialRelationState": relation_number
                        }

                if child_table not in object_relations:
                    object_relations[child_table] = [relation_entry]
                else:
                    existing_table_relations = object_relations[child_table]
                    existing_relation_updated = False
                    for existing_relation in existing_table_relations:
                        if (existing_relation.get("ChildTable", None) == child_table  
                            and existing_relation.get("ChildColumn", None) == child_column):
                                existing_relation["Relation"] += relation_number
                                existing_relation["InitialRelationState"] += relation_number
                                if existing_relation["Relation"] > 7:
                                    existing_relation["Relation"] = 7
                                    existing_relation["InitialRelationState"] = 7
                                existing_relation_updated = True
                    if not existing_relation_updated:
                        existing_table_relations.append(relation_entry)
        relations_sorted = dict(sorted(object_relations.items())) 
        return relations_sorted

    @xml_object_relations.setter
    def xml_object_relations(self, relations_data):
        self._object_relations = relations_data
        self.reset_container_relations()

    def binary2int(self, binary): 
        int_val, i, n = 0, 0, 0
        while(binary != 0): 
            a = binary % 10
            int_val = int_val + a * pow(2, i) 
            binary = binary // 10
            i += 1
        return int_val

    def reset_container_relations(self):
        # print("reset relations")
        table_relations = self._object_relations
        if self.object_relations_node:
            for element in self.object_relations_node.data.getchildren():
                self.object_relations_node.data.remove(element)

        local_relation_list = []
        
        if table_relations is not None:
            if isinstance(table_relations, list):
                table_relations = {self.table_name: table_relations}
                self.xml_object_relations = table_relations
                return True

            for relation_table, relations in table_relations.items():
                for relation in relations:
                    if relation["Relation"] > 0:
                        relation_keys = self.get_relation_keys(relation)
                        for relation_key in relation_keys:
                            if relation_key not in local_relation_list:
                                local_relation_list.append(relation_key)
                                relation_object = object_parameter(self, "Relation", relation_key)
                                self.object_relations_node.xml_append_node(relation_object)
            return True
        return False

    def get_relation_keys(self, relation):
        relation_type = relation["Relation"]
        relation_keys = []

        table_name = relation["ChildTable"]
        column_name = relation["ChildColumn"]

        prefix = f"{table_name}|{column_name}|"

        if relation_type in [1, 3]:
            relation_keys.append(f"{prefix}FK") 
        if relation_type in [2, 3]:
            relation_keys.append(f"{prefix}CR")
        if relation_type in [5, 7]:
            relation_keys.append(f"{prefix}FK, IgnoreInSupersetHandling")
        if relation_type in [6, 7]:
            relation_keys.append(f"{prefix}CR, IgnoreInSupersetHandling")

        return relation_keys
        
    @property
    def delete_residuals(self):
        if self.delete_residuals_node and self.delete_residuals_node.data.text.isnumeric():
            return int(self.delete_residuals_node.text)
        return 0

    def set_delete_residuals(self, status):
        self.delete_residuals_node.text = status

