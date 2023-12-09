from lxml import etree

class transport_template_custom_object(object):

    def __init__(self, parent, node_class, source_element=None, xml_object_class=None):
        super(transport_template_custom_object, self).__init__()

        self._parent = parent
        self._xml_object_class = node_class
        self._table_name = None
        self._key_column = None
        if xml_object_class:
            self._xml_object_class = xml_object_class
        self._state = 0
        self._option = ""
        self.data = source_element
        if self.data is not None:
            self.data.tail = None

        """ Node setup for new objects """
        if source_element is None:
            self.data = etree.Element(node_class)
            self.data.tag = node_class
            self.data.text = None
            self.data.tail = None

        self._display = "\n".join(self.data.itertext()).strip()
        self._description = ""

        if self._parent is not None and isinstance(self._parent, transport_template_custom_object) and source_element is None:
            self._parent.xml_append_node(self)
    
    @property
    def parent(self):
        return self._parent
        
    @property
    def xml_object_class(self):
        return self._xml_object_class

    @property
    def table_name(self):
        return self._table_name
    
    @table_name.setter
    def table_name(self, value):
        self._table_name = value
    
    @property
    def key_column(self):
        return self._key_column
    
    @key_column.setter
    def key_column(self, value):
        self._key_column = value

    @property
    def accepted_classes(self):
        # define what class is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all objects 
        return []

    @property
    def accepted_tables(self):
        # define what table is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all tables 
        return []

    @property
    def string(self):
        etree.indent(self.data)
        return etree.tostring(self.data, pretty_print=True, encoding='UTF-8', method="xml").decode('UTF-8')

    @property
    def display(self):
        return self._display

    @display.setter
    def display(self, value):
        self._display = value

    @property
    def display(self):
        xml_display = self.xml_get_attribute("Display")
        if xml_display:
            return xml_display
        return self._display

    @display.setter
    def display(self, value):
        self.xml_set_attribute("Display", value)
        self._display = value


    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        self._description = value
        
    @property
    def text(self):
        return self.data.text
    
    @property
    def option(self):
        return self._option
    
    @option.setter
    def option(self, value):
        self._option = value

    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, value):
        self._state = value

    @text.setter
    def text(self, value):
        self.data.text = str(value)

    def xml_find_parent(self, element, class_lookup):
        parent_node = element.getparent()
        if parent_node is not None:
            if parent_node.tag == class_lookup:
                return parent_node
            return self.xml_find_parent(parent_node, class_lookup)
        else:
            return None

    def xml_find_children(self, element, class_lookup):
        target_node = element.find(class_lookup)
        if target_node is not None:
            return target_node.getchildren()
        return None
    
    def xml_find_child(self, element, class_lookup):
        target_node = element.find(class_lookup)
        if target_node is not None:
            return target_node
        return None
    
    def xml_get_child(self, class_lookup, parent_element=None):
        if parent_element is None:
            parent_element = self.data
        child_element = self.xml_find_child(parent_element, class_lookup)
        return child_element

    def xml_get_children(self, class_lookup=None, parent_element=None):
        child_objects = []

        if parent_element is None:
            parent_element = self.data

        child_elements = parent_element.getchildren()

        if class_lookup is not None:
            child_elements = self.xml_find_children(parent_element, class_lookup)
        if child_elements is not None:
            for element in child_elements:
                if not isinstance(element, etree._Comment) and isinstance(element, etree._Element):
                    child_objects.append(element)
        return child_objects

    def xml_delete_object(self):
        parent_node = self.data.getparent()
        previous_node = self.data.getprevious()

        if isinstance(previous_node, etree._Comment):
            parent_node.remove(previous_node)

        if parent_node is not None:
            parent_node.remove(self.data)
        
        return True

    def xml_get_attribute(self, attribute):
        value = ""
        if attribute in self.data.attrib.keys():
            value = self.data.attrib[attribute]
        return value

    def xml_set_attribute(self, attribute, value):
        self.data.attrib[attribute] = str(value)

    def xml_append_node(self, node_object, root_object=None):
        if root_object is None:
            root_object = self.data

        if root_object == node_object:
            return False

        if root_object is not None and isinstance(node_object, etree._Element):
            root_object.append(node_object)
            return True
        
        if root_object is not None and isinstance(node_object, transport_template_custom_object):
            root_object.append(node_object.data)
    
    def xml_remove_children(self, element=None):
        if element is None:
            element = self.data
        
        if isinstance(element, transport_template_custom_object):
            element = element.data

        for child_element in element.getchildren():
            element.remove(child_element)

    def children(self):
        return self.xml_get_children()
    
    def xml_add_child_node(self, object_info_dict):
        pass

    def xml_get_parameter(self, parameter_name, source_data=None):
        if source_data is not None:
            child_nodes = self.xml_get_children(parent_element=source_data)
        else:
            child_nodes = self.xml_get_children()
        
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name is not None and node_name == parameter_name:
                return node
        return None
    
    def prepare_export_data(self):
        return self.string