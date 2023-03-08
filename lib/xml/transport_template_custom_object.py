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
        return etree.tostring(self.data, pretty_print=True, encoding='UTF-8').decode('UTF-8')

    @property
    def description(self):
        return None
        
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
                if not isinstance(element, etree._Comment) and isinstance(element, etree._Element):
                    child_objects.append(element)
        return child_objects

    def refresh_xml_preview(self):
        self.application.xml_structure_changed.emit()

    def delete_object(self):
        parent_node = self.data.getparent()
        previous_node = self.data.getprevious()

        if parent_node is not None:
            parent_node.remove(self.data)
        
        if isinstance(previous_node, etree._Comment):
            parent_node.remove(previous_node)
        return True

    def get_attribute(self, attribute):
        value = ""
        if attribute in self.data.attrib.keys():
            value = self.data.attrib[attribute]
        return value

    def set_attribute_value(self, attribute, value, refresh=True):
        self.data.attrib[attribute] = str(value)
        if refresh:
            self.refresh()

    def append(self, node_object):
        if isinstance(node_object, etree._Element):
            self.data.append(node_object)
            return True
        
        if isinstance(node_object, transport_template_custom_object):
            self.data.append(node_object.data)
    
    def delete_child_items(self, element=None):
        if element is None:
            element = self.data

        for child_element in element.getchildren():
            element.remove(child_element)

    def set_text(self, value):
        self.data.text = str(value)

    @property
    def text(self):
        return self.data.text