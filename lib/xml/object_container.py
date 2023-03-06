from lxml import etree
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_parameter import object_parameter
import numbers
            
class object_container(transport_template_custom_object):
    def __init__(self, application, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations=[]):
        super(object_container, self).__init__(application=application, node_class="Parameter", source_element=source_element)
        self.relations = relations
        self.table_name = base_table
        self.display_name = display_name
        self.pk_columns = pk_columns
        self.base_object_node = None
        self.delete_residuals_node = None
        self.object_relations_node = None


        """ Main Container Node setup"""
        if source_element is None:
            self.data.attrib['Name'] = "Container"

            """ Container transport settings """
            self.delete_residuals_node = object_parameter(self.application, "DeleteResiduals", delete_residual_objects)

            """ Add selected Transport relations """
            self.object_relations_node = object_parameter(self.application, "Relations")

            self.base_object_node = object_parameter(self.application, "BaseObject")

            base_object_table = object_parameter(self.application, "Tablename", base_table)
            base_object_display = object_parameter(self.application, "Display", display_name)
            
            """ build the object container """
            self.base_object_node.append(base_object_table)
            self.base_object_node.append(base_object_display)

            base_object_columns = object_parameter(self.application, "Columns")
            for pk_column, pk_column_value in pk_columns.items():
                if pk_column is not None:
                    base_object_column = object_parameter(self.application, pk_column, pk_column_value)
                    base_object_columns.append(base_object_column)

            self.base_object_node.append(base_object_columns)

            """ attach container to the xml structure"""
            self.append(self.base_object_node)
            self.append(self.delete_residuals_node)
            self.append(self.object_relations_node)

            self.reset_container_relations()

        else:
            """ load data from source element """
            for element in self.get_child_objects():
                if element.attrib["Name"] == "BaseObject":
                    self.base_object_node = object_parameter(self.application, "BaseObject", source_element=element)
                if element.attrib["Name"] == "DeleteResiduals":
                    self.delete_residuals_node = object_parameter(self.application, "DeleteResiduals", source_element=element)
                if element.attrib["Name"] == "Relations":
                    self.object_relations_node = object_parameter(self.application, "Relations", source_element=element)

    @property
    def description(self):
        container_description = etree.Comment(f"({self.table_name}) - ({self.display_name})")
        return container_description

    def reset_container_relations(self):
        table_relations = self.relations

        for element in self.object_relations_node.data.getchildren():
            self.object_relations_node.data.remove(element)

        local_relation_list = []
        
        if table_relations is not None:
            for relation in table_relations:
                if relation["Relation"] > 0:
                    relation_keys = self.get_relation_keys(relation)
                    for relation_key in relation_keys:
                        if relation_key not in local_relation_list:
                            local_relation_list.append(relation_key)
                            relation_object = object_parameter(self.application, "Relation", relation_key)
                            self.object_relations_node.append(relation_object)
            # self.application.load_xml_preview()
            return True
        # self.application.load_xml_preview()
        return False

    def get_relation_keys(self, relation):
        relation_type = relation["Relation"]
        relation_keys = []

        table_group_name = relation["TableGroup"]

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
        if isinstance(self.delete_residuals_node.data.text, numbers.Number):
            return int(self.delete_residuals_node.data.text)
        return 0

    def set_delete_residuals(self, status):
        self.delete_residuals_node.set_text(status)
        self.refresh_xml_preview()

