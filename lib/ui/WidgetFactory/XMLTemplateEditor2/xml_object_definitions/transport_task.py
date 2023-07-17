from ..xml_object_definitions import *

class transport_task(transport_template_custom_object):
    
    def __init__(self, application, object_class, source_element=None):
        super(transport_task, self).__init__(application=application, node_class="Task", source_element=source_element)
        
        """ Task Node setup"""
        if source_element is not None:
            self.data = source_element
        else:
            self.data.attrib["Class"] = object_class

            if object_class == "VI.Transport.ObjectTransport, VI.Transport":
                self.data.attrib["Display"] = "Object Transport Task"

    def add_container(self, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations=[]):
        container = object_container(self.application, source_element, base_table, display_name, delete_residual_objects, pk_columns, relations)
        if container.description is not None:
            self.append(container.description)
        self.append(container)
        return container
    
    @property
    def display(self):
        return self.xml_get_attribute("Display")

    def children(self):
        task_nodes = self.data.getchildren()
        child_objects = []
        if task_nodes:
            for task in task_nodes:
                if not isinstance(task, etree._Comment) and isinstance(task, etree._Element):
                    task_type = task.attrib.get("Name", None)
                    xml_obj = None
                    if task_type:
                        if task_type == "Container":
                            xml_obj = object_container(self.application, task)
                        
                    if xml_obj:
                        child_objects.append(xml_obj)
        return child_objects
    

class sql_script_transport_task(transport_task):
    
    def __init__(self, application, object_class, source_element=None):
        super(sql_script_transport_task, self).__init__(application=application, object_class=object_class, source_element=source_element)
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