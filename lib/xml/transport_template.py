from lxml import etree
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_parameter import object_parameter
from lib.xml.transport_task import transport_task, sql_script_transport_task

class transport_template(transport_template_custom_object):

    def __init__(self, application, source_element=None):
        super(transport_template, self).__init__(application=application, node_class="TransportTemplate", source_element=source_element)

        self.data.attrib["Version"] = "1.0"

        """ Tranport Header setup """
        header = etree.Element("Header")

        """ Transport description setup """
        self.transport_description = object_parameter(self.application, "Description", "Transport Template Description")

        header.append(self.transport_description.data)

        tasks_root = etree.Element("Tasks")

        """ Build the transport structure blocks """
        self.append(header)
        self.append(tasks_root)

    def add_transport_task(self, task_class):
        task_obj = None
        if task_class == "VI.Transport.ObjectTransport, VI.Transport":
            task_obj = transport_task(self.application, task_class)
        elif task_class == "VI.Transport.SQLTransport, VI.Transport":
            task_obj = sql_script_transport_task(self.application, task_class)
        else:
            task_obj = transport_task(self.application, task_class)

        if task_obj:
            self.tasks_root.append(task_obj.data)
            return task_obj
    
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
                if not isinstance(task, etree._Comment) and isinstance(task, etree._Element):
                    task_type = task.attrib.get("Class", None)
                    if task_type:
                        if task_type == "VI.Transport.ObjectTransport, VI.Transport":
                            task_obj = transport_task(self.application, task_type, task)
                        if task_type == "VI.Transport.SQLTransport, VI.Transport":
                            task_obj = sql_script_transport_task(self.application, task_type, task)
                        else:
                            task_obj = transport_task(self.application, task_type, task)
                    if task_obj:
                        task_list.append(task_obj)
        return task_list

    @property
    def header(self):
        return self.find_child(self.data, "Header")

    def parse_xml_file(self, xml_file):
        if not xml_file:
            return False

        xml_parser = etree.XMLParser(remove_comments=False, remove_blank_text=True)
        try:
            xmlObj = etree.parse(xml_file, parser=xml_parser)
        except:
            #TODO: fix temporary handling of file parsing issues
            self.application.new_transport_template(xml_file)
            return False

        if xmlObj is not None:
            self.data = xmlObj
            self.application.xml_structure_changed.emit()
            self.application.reload_xml_structure()