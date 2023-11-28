from lxml import etree
from .transport_template_custom_object import transport_template_custom_object
from .object_parameter import object_parameter
from .transport_task import transport_task, sql_script_transport_task

class transport_template(transport_template_custom_object):

    def __init__(self, parent, source_element=None):
        super(transport_template, self).__init__(parent=parent, node_class="TransportTemplate", source_element=source_element)

        self.data.attrib["Version"] = "1.0"

        """ Tranport Header setup """
        header = etree.Element("Header")

        """ Transport description setup """
        self.transport_description = object_parameter(self.parent, "Description", "Transport Template Description")

        header.append(self.transport_description.data)

        tasks_root = etree.Element("Tasks")

        """ Build the transport structure blocks """
        super().xml_append_node(header)
        super().xml_append_node(tasks_root)

    @property
    def xml_object_class(self):
        return "Transport_Template"

    def add_transport_task(self, task_class):
        task_obj = None
        if task_class == "VI.Transport.ObjectTransport, VI.Transport":
            task_obj = transport_task(self.parent, task_class)
        elif task_class == "VI.Transport.SQLTransport, VI.Transport":
            task_obj = sql_script_transport_task(self.parent, task_class)
        else:
            task_obj = transport_task(self.parent, task_class)

        if task_obj:
            self.tasks_root.append(task_obj.data)
            return task_obj

    @property
    def tasks_root(self):
        return self.xml_find_child(self.data, "Tasks")
    
    def children(self):
        task_nodes = self.xml_find_children(self.data, "Tasks")
        task_list = []
        if task_nodes:
            for task in task_nodes:
                if not isinstance(task, etree._Comment) and isinstance(task, etree._Element):
                    task_type = task.attrib.get("Class", None)
                    if task_type:
                        if task_type == "VI.Transport.ObjectTransport, VI.Transport":
                            task_obj = transport_task(self.parent, task_type, task)
                        if task_type == "VI.Transport.SQLTransport, VI.Transport":
                            task_obj = sql_script_transport_task(self.parent, task_type, task)
                        else:
                            task_obj = transport_task(self.parent, task_type, task)
                    if task_obj:
                        task_list.append(task_obj)
        return task_list

    @property
    def header(self):
        return self.xml_find_child(self.data, "Header")

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
            # self.parent.XMLTemplateEditor.xml_structure_changed.emit(xml_file)
            # self.parent.XMLTemplateEditor.reload_xml_structure()
            return True, "XML data parsing successful!"
        return False, "XML Parsing error not handled"

    def xml_remove_children(self):
        super().xml_remove_children(self.tasks_root)

    def xml_append_node(self, node_object):
        if isinstance(node_object, etree._Element):
            self.tasks_root.append(node_object)
            return True
        
        if isinstance(node_object, transport_template_custom_object):
            self.tasks_root.append(node_object.data)
