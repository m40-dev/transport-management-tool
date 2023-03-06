from lxml import etree
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_container import object_container


class transport_task(transport_template_custom_object):
    
    def __init__(self, application, task_class, source_element=None):
        super(transport_task, self).__init__(application=application, node_class="Task", source_element=source_element)
        self.task_class = task_class

        """ Task Node setup"""
        if source_element is not None:
            self.data = source_element
        else:
            self.data.attrib["Display"] = self.task_class

            if self.task_class == "ObjectTransport":
                self.data.attrib["Class"] = "VI.Transport.ObjectTransport, VI.Transport"

    def add_container(self, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations=[]):
        container = object_container(self.application, source_element, base_table, display_name, delete_residual_objects, pk_columns, relations)
        if container.description is not None:
            self.append(container.description)
        self.append(container)
        return container

    @property
    def task_containers(self):
        return self.get_child_objects()
