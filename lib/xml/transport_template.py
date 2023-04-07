from lxml import etree
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_parameter import object_parameter
from lib.xml.transport_task import transport_task

class transport_template(transport_template_custom_object):

    def __init__(self, application, source_element=None):
        super(transport_template, self).__init__(application=application, node_class="TransportTemplate", source_element=source_element)

        self.data.attrib["Version"] = "1.0"

        """ Tranport Header setup """
        header = etree.Element("Header")

        """ Transport description setup """
        transport_description = object_parameter(self.application, "Description", "Transport Template Editor Test")

        header.append(transport_description.data)

        tasks_root = etree.Element("Tasks")

        """ Build the transport structure blocks """
        self.append(header)
        self.append(tasks_root)

    def add_transport_task(self, task_class):
        new_task = transport_task(self.application, task_class)
        self.tasks_root.append(new_task.data)
        return new_task
    
    def clear_xml_tasks(self):
        self.delete_child_items(self.tasks_root)

    @property
    def tasks_root(self):
        return self.find_child(self.data, "Tasks")
    
    @property
    def tasks(self):
        task_nodes = self.find_children(self.data, "Tasks")
        task_list = []
        if task_nodes:
            for task in task_nodes:
                task_obj = transport_task(self.application, task.attrib["Display"], task)
                task_list.append(task_obj)
        return task_list

    @property
    def header(self):
        return self.find_child(self.data, "Header")

    def parse_xml_file(self, xml_file):
        if not xml_file:
            return False

        xml_parser = etree.XMLParser(remove_comments=False, remove_blank_text=True)
        xmlObj = etree.parse(xml_file, parser=xml_parser)

        if xmlObj is not None:
            self.data = xmlObj
            self.application.xml_structure_changed.emit()
            self.application.reload_xml_structure()