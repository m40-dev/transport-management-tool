from lxml import etree
from ..xml_object_definitions import transport_template_custom_object, object_parameter, TASKS, transport_task


class transport_template(transport_template_custom_object):

    def __init__(self, parent, source_element=None):
        super(transport_template, self).__init__(parent=parent, node_class="TransportTemplate", source_element=source_element)
        self.xml_set_attribute("Version", "1.0")
        self.remap_XML_nodes(reassign=True)


    def remap_XML_nodes(self, reassign=False):
        header_xml = self.xml_find_child(self.data, "Header")
        self.header_node = transport_template_custom_object(parent=self, node_class="Header", source_element=header_xml)
        
        description_xml = self.xml_get_parameter("Description", self.header_node.data)
        self.transport_description = object_parameter(self.header_node, "Description", "Transport Template Description", source_element=description_xml)

        tasks_xml = self.xml_find_child(self.data, "Tasks")
        self.tasks_root = transport_template_custom_object(parent=self, node_class="Tasks", source_element=tasks_xml)
        
        if reassign:
            super().xml_append_node(self.header_node)
            super().xml_append_node(self.tasks_root)

    @property
    def xml_object_class(self):
        return "Transport_Template"

    def add_transport_task(self, task_class):
        task_obj = None
        xml_object_class = TASKS.get(task_class, None)

        if xml_object_class:
            # map the object class with the supported dictionary
            task_obj = xml_object_class(self, task_class)
        else:
            # fallback to the default transport task, whatever it might be so even unsupported classes get listed and can be saved back
            task_obj = transport_task(self, task_class)

        if task_obj:
            # self.xml_append_node(task_obj)
            return task_obj
    
    def children(self):
        task_nodes = self.tasks_root.xml_get_children()
        task_list = []
        if task_nodes:
            for task in task_nodes:
                if not isinstance(task, etree._Comment) and isinstance(task, etree._Element):
                    task_obj = None
                    task_class = task.attrib.get("Class", None)
                    if task_class:
                        xml_object_class = TASKS.get(task_class, None)
                        if xml_object_class:
                            # map the object class with the supported dictionary
                            task_obj = xml_object_class(self.tasks_root, task_class, task)
                        else:
                            # fallback to the default transport task, whatever it might be so even unsupported classes get listed and can be saved back
                            task_obj = transport_task(self.tasks_root, task_class, task)
                    if task_obj:
                        task_list.append(task_obj)
        return task_list

    @property
    def xml_tasks_root(self):
        return self.xml_find_child(self.data, "Tasks")

    def parse_xml_file(self, xml_file=None):
        if not xml_file:
            return False, "XML File to parse was not provided"
        xmlObj = None
        xml_parser = etree.XMLParser(remove_comments=False, remove_blank_text=True)
        try:
            xmlObj = etree.parse(xml_file, parser=xml_parser)
        except etree.XMLSyntaxError as ex:
            # syntax errors will be returned to the calling method which can then show error message
            return False, ex.msg

        if xmlObj is not None:
            self.data = xmlObj
            self.remap_XML_nodes()
            return True, "XML data parsing successful!"
        return False, "XML Parsing error not handled"

    def xml_remove_children(self):
        super().xml_remove_children(self.tasks_root)

    def xml_append_node(self, node_object):
        if self.xml_tasks_root is None:
            return False

        if isinstance(node_object, etree._Element):
            self.xml_tasks_root.append(node_object)
            return True
        
        if isinstance(node_object, transport_template_custom_object):
            self.xml_tasks_root.append(node_object.data)