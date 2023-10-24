from ..xml_object_definitions import *

class transport_task(transport_template_custom_object):
    
    def __init__(self, parent, object_class="VI.Transport.ObjectTransport, VI.Transport", source_element=None):
        super(transport_task, self).__init__(parent=parent, node_class="Task", source_element=source_element)
        
        """ Task Node setup"""
        if source_element is not None:
            self.data = source_element
        else:
            self.data.attrib["Class"] = object_class

            if object_class == "VI.Transport.ObjectTransport, VI.Transport":
                self.data.attrib["Display"] = "Object Transport Task"

    def add_container(self, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations=[]):
        container = object_container(self.parent, source_element, base_table, display_name, delete_residual_objects, pk_columns, relations)
        if container.description is not None:
            self.xml_append_node(container.description)
        self.xml_append_node(container)
        return container

    @property
    def xml_object_class(self):
        return "Object_Transport_Task"

    @property
    def display(self):
        return self.xml_get_attribute("Display")

    @display.setter
    def display(self, value):
        self.xml_set_attribute("Display", value)

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
                            xml_obj = object_container(self.parent, task)
                        
                    if xml_obj:
                        child_objects.append(xml_obj)
        return child_objects
    
    def xml_add_child_node(self, object_info_dict, row=-1):
        print("add child to transport task")
        base_table = object_info_dict.get("table_name", None)
        display_name = object_info_dict.get("object_display", None)
        pk_columns = object_info_dict.get("pk_columns", None)
        xml_obj = object_container(parent=self.parent, base_table=base_table, display_name=display_name, pk_columns=pk_columns)
        return xml_obj


class sql_script_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.SQLTransport, VI.Transport", source_element=None):
        super(sql_script_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        self._option = "Run At Start"
        if source_element is None:
            self.data.attrib["Display"] = "SQL Script Transport"
            self.set_pre_import(0)

    @property
    def state(self):
        value = self.pre_import 
        if value > 0:
            value = 2
        return value
    
    @state.setter
    def state(self, value):
        if value > 0:
            value = 1
        self.set_pre_import(value)

    @property
    def xml_object_class(self):
        return "SQL_Transport_Task"

    @property
    def pre_import(self):
        child_nodes = self.xml_get_children()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "PreImport" and node.text.isnumeric():
                return int(node.text)
        return 0

    def set_pre_import(self, status):
        node_found = False
        child_nodes = self.xml_get_children()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "PreImport":
                node.text = str(status)
                node_found = True
        if not node_found:
            parameter = object_parameter(self.parent, "PreImport", str(status))
            self.xml_append_node(parameter)

    def add_sql_script(self, script_type):
        sql_script_node = sql_script_container(self.parent, script_type=script_type)
        self.xml_append_node(sql_script_node)
        return sql_script_node
    
    @property
    def common_sql(self):
        child_nodes = self.xml_get_children()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "CommonSQL":
                return sql_script_container(self.parent, source_element=node, script_type=node_name)
        return None
    
    @property
    def payload_sql(self):
        child_nodes = self.xml_get_children()
        for node in child_nodes:
            node_name = node.attrib.get("Name", None)
            if node_name and node_name == "PayloadSQL":
                return sql_script_container(self.parent, source_element=node, script_type=node_name)
        return None

    def children(self):
        task_nodes = self.data.getchildren()
        child_objects = []
        if task_nodes:
            for task in task_nodes:
                if not isinstance(task, etree._Comment) and isinstance(task, etree._Element):
                    task_type = task.attrib.get("Name", None)
                    xml_obj = None
                    if task_type:
                        if task_type in ["PayloadSQL", "CommonSQL"]:
                            xml_obj = sql_script_container(self.parent, task)
                            if xml_obj:
                                child_objects.append(xml_obj)
        return child_objects