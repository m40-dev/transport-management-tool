from lxml import etree
from .transport_task import transport_task
from .task_containers.sql_script_container import sql_script_container
from ..object_parameter import object_parameter


class sql_script_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.SQLTransport, VI.Transport", source_element=None):
        super(sql_script_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        # self._parent = parent
        self._option = "Run At Start"
        if source_element is None:
            self.xml_set_attribute("Display", "SQL Script Transport")

        self.remap_XML_nodes(reassign=True)

    def remap_XML_nodes(self, reassign=False):
        xml_pre_import = self.xml_get_parameter("PreImport")
        self.pre_import = object_parameter(self, "PreImport", 0, xml_pre_import)

        xml_common_sql = self.xml_get_parameter("CommonSQL")
        self.common_sql = object_parameter(self, "CommonSQL", "", xml_common_sql)

        xml_payload_sql = self.xml_get_parameter("PayloadSQL")
        self.payload_sql = object_parameter(self, "PayloadSQL", "", xml_payload_sql)

    @property
    def accepted_classes(self):
        # define what class is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all objects 
        return ["Transport_SQL_Object"]

    @property
    def state(self):
        value = 0
        if len(self.pre_import.text.strip()) > 0:
            if self.pre_import.text.isnumeric():
                value = int(self.pre_import.text)
        if value > 0:
            value = 2
        return value
    
    @state.setter
    def state(self, value):
        if value > 0:
            value = 1
        self.pre_import.text = str(value)

    def add_sql_script(self, script_type):
        sql_script_node = sql_script_container(self, script_type=script_type)
        self.xml_append_node(sql_script_node)
        return sql_script_node

    def children(self):
        task_nodes = self.xml_get_children()
        child_objects = []
        for task in task_nodes:
            if not isinstance(task, etree._Comment) and isinstance(task, etree._Element):
                task_type = task.attrib.get("Name", None)
                xml_obj = None
                if task_type:
                    if task_type in ["PayloadSQL", "CommonSQL"]:
                        xml_obj = sql_script_container(parent=self, source_element=task)
                        if xml_obj:
                            child_objects.append(xml_obj)
        return child_objects

    def prepare_export_data(self):
        self.xml_append_node(self.pre_import)
        return self.string