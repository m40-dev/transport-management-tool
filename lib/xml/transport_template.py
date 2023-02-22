from lxml import etree

class transport_template_custom_object(object):

    def __init__(self, application, node_class, source_element=None):
        super(transport_template_custom_object, self).__init__()
        self.application=application
        self.data = None

        """ Node setup for new objects """
        if source_element is None:
            self.data = etree.Element(node_class)
            self.data.tag = node_class
            self.data.text = None
            self.data.tail = None
        else:
            self.data = source_element

    @property
    def string(self):
        etree.indent(self.data)
        return etree.tostring(self.data, pretty_print=True, encoding='UTF-8', xml_declaration=True).decode('UTF-8')
        
    def find_parent(self, element, class_lookup):
        parent_node = element.getparent()
        if parent_node is not None:
            if parent_node.tag == class_lookup:
                return parent_node
            return self.find_parent(parent_node, class_lookup)
        else:
            return None

    def find_children(self, element, class_lookup):
        target_node = element.find(class_lookup)
        if target_node is not None:
            return target_node.getchildren()
        return None
    
    def find_child(self, element, class_lookup):
        target_node = element.find(class_lookup)
        if target_node is not None:
            return target_node
        return None
    
    def get_child_object(self, class_lookup, parent_element=None):
        if parent_element is None:
            parent_element = self.data
        child_element = self.find_child(parent_element, class_lookup)
        return child_element

    def get_child_objects(self, class_lookup=None, parent_element=None):
        child_objects = []

        if parent_element is None:
            parent_element = self.data

        child_elements = parent_element.getchildren()

        if class_lookup is not None:
            child_elements = self.find_children(parent_element, class_lookup)
        if child_elements is not None:
            for element in child_elements:
                child_objects.append(element)
        return child_objects

    def refresh(self):
        self.application.refresh_widget.emit(self.data)

    def delete_object(self):
        parent_node = self.data.getparent()
        if parent_node is not None:
            parent_node.remove(self.data)
        return True

    def get_attribute(self, attribute):
        value = ""
        if attribute in self.data.attrib.keys():
            value = self.data.attrib[attribute]
        return value

    def set_attribute_value(self, attribute, value, refresh=True):
        self.data.attrib[attribute] = str(value)
        #TODO: enable when all data is accessed via the cd objects
        # if str(value) == "":
        #     self.data.attrib.pop(attribute)
        if refresh:
            self.refresh()

    def append(self, node_object):
        if isinstance(node_object, etree._Element):
            self.data.append(node_object)
            return True
        
        if isinstance(node_object, transport_template_custom_object):
            self.data.append(node_object.data)
    

class transport_template(transport_template_custom_object):

    def __init__(self, application, source_element=None):
        super(transport_template, self).__init__(application=application, node_class="TransportTemplate", source_element=source_element)

        self.tasks = {}

        self.data.attrib["Version"] = "1.0"

        """ Tranport Header setup """
        self.header = etree.Element("Header")

        """ Transport description setup """
        self.description = object_parameter(self.application, "Description", "Transport Template Editor Test")

        self.header.append(self.description.data)

        self.tasks = etree.Element("Tasks")

        """ Build the transport structure blocks """
        self.append(self.header)
        self.append(self.tasks)

    def add_transport_task(self, task_class):
        new_task = transport_task(self.application, task_class)
        self.tasks.append(new_task.data)
        return new_task
    

class transport_task(transport_template_custom_object):
    
    def __init__(self, application, task_class, source_element=None):
        super(transport_task, self).__init__(application=application, node_class="Task", source_element=source_element)
        self.task_class = task_class

        """ Task Node setup"""
        self.data.attrib["Display"] = self.task_class

        if self.task_class == "ObjectTransport":
            self.data.attrib["Class"] = "VI.Transport.ObjectTransport, VI.Transport"

    def add_container(self, base_object):
        container = object_container(self.application, base_object)
        if container.description is not None:
            self.append(container.description)
        self.append(container)
        return container
            
class object_container(transport_template_custom_object):
    def __init__(self, application, base_object, source_element=None):
        super(object_container, self).__init__(application=application, node_class="Parameter", source_element=source_element)
        self.base_object = base_object

        """ Main Container Node setup"""

        self.data.attrib['Name'] = "Container"

        base_object_node = object_parameter(self.application, "BaseObject")
        base_object_table = object_parameter(self.application, "Tablename", base_object.table_name)
        base_object_display = object_parameter(self.application, "Display", base_object.display_name)
        
        """ build the object container """
        base_object_node.append(base_object_table)
        base_object_node.append(base_object_display)

        base_object_columns = object_parameter(self.application, "Columns")
        for pk_column in base_object.pk_columns:
            if pk_column is not None:
                base_object_column = object_parameter(self.application, pk_column, base_object.get_value(pk_column))
                base_object_columns.append(base_object_column)

        base_object_node.append(base_object_columns)

        """ Container transport settings """
        self.delete_residuals = object_parameter(self.application, "DeleteResiduals", base_object.delete_residual_objects)

        """ Add selected Transport relations """
        self.object_relations = object_parameter(self.application, "Relations")
        
        """ attach container to the xml structure"""
        self.append(base_object_node)
        self.append(self.delete_residuals)
        self.append(self.object_relations)

        self.reset_container_relations()

    @property
    def description(self):
        container_description = etree.Comment(f"({self.base_object.table_name}) - ({self.base_object.display_name})")
        return container_description

    def reset_container_relations(self):
        table_relations = self.base_object.object_relations
        local_relation_list = []
        
        if table_relations is not None:
            print("table relations", table_relations)
            for relation in table_relations:
                print(relation)
                relation_keys = self.get_relation_keys(relation)
                for relation_key in relation_keys:
                    if relation_key not in local_relation_list:
                        print(relation_key)
                        local_relation_list.append(relation_key)
                        relation_object = object_parameter(self.application, "Relation", relation_key)
                        self.object_relations.append(relation_object)
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
        if relation_type == 3:
            relation_keys.append(f"{prefix}CR")
        if relation_type == 5:
            relation_keys.append(f"{prefix}FK, IgnoreSupersetHandling")

        return relation_keys


class object_parameter(transport_template_custom_object):
    def __init__(self, application, parameter_name, parameter_value="", source_element=None,):
        super(object_parameter, self).__init__(application=application, node_class="Parameter", source_element=source_element)

        """ Container Node setup"""
        self.data.attrib["Name"] = parameter_name
        self.data.text = parameter_value
