from lxml import etree
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_container import object_container
from lib.xml.sql_script_container import sql_script_container
from lib.xml.object_parameter import object_parameter


class transport_task(transport_template_custom_object):
    
    def __init__(self, application, task_class, source_element=None):
        super(transport_task, self).__init__(application=application, node_class="Task", source_element=source_element)
        

        """ Task Node setup"""
        if source_element is not None:
            self.data = source_element
        else:
            self.data.attrib["Class"] = task_class

            if task_class == "VI.Transport.ObjectTransport, VI.Transport":
                self.data.attrib["Display"] = "Object Transport Task"
            

    def add_container(self, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations=[]):
        container = object_container(self.application, source_element, base_table, display_name, delete_residual_objects, pk_columns, relations)
        if container.description is not None:
            self.append(container.description)
        self.append(container)
        return container

    @property
    def task_containers(self):
        return self.get_child_objects()
    
    @property
    def task_display(self):
        return self.get_attribute("Display")
    
    @property
    def task_class(self):
        return self.get_attribute("Class")
    

class sql_script_transport_task(transport_task):
    
    def __init__(self, application, task_class, source_element=None):
        super(sql_script_transport_task, self).__init__(application=application, task_class=task_class, source_element=source_element)
        if source_element is None:
            self.data.attrib["Display"] = "SQL Script Transport"
            self.set_pre_import(0)


    @property
    def pre_import(self):
        child_nodes = self.get_child_objects()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "PreImport":
                return int(node.text)

    def set_pre_import(self, status):
        node_found = False
        child_nodes = self.get_child_objects()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "PreImport":
                node.text = str(status)
                node_found = True
        if not node_found:
            parameter = object_parameter(self.application, "PreImport", str(status))
            self.append(parameter)

    def add_sql_script(self, script_type):
        sql_script_node = sql_script_container(self.application, script_type=script_type)
        self.append(sql_script_node)
        return sql_script_node
    
    @property
    def common_sql(self):
        child_nodes = self.get_child_objects()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "CommonSQL":
                return sql_script_container(self.application, source_element=node, script_type=node_name)
        return None
    
    @property
    def payload_sql(self):
        child_nodes = self.get_child_objects()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "PayloadSQL":
                return sql_script_container(self.application, source_element=node, script_type=node_name)
        return None