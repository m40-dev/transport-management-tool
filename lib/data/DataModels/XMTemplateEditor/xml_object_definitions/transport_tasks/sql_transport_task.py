from lxml import etree
from .transport_task import transport_task
from .task_containers.sql_script_container import sql_script_container
from ..object_parameter import object_parameter


class sql_script_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.SQLTransport, VI.Transport", source_element=None):
        super(sql_script_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        self._option = "Run At Start"
        if source_element is None:
            self.data.attrib["Display"] = "SQL Script Transport"
            self.set_pre_import(0)

    @property
    def accepted_classes(self):
        # define what class is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all objects 
        return ["Transport_SQL_Object"]

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
