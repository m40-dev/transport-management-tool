from lxml import etree
from .transport_task import transport_task
from .task_containers.object_container import object_container

class object_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.ObjectTransport, VI.Transport", source_element=None):
        super(object_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        
        if source_element is None:
            self.data.attrib["Display"] = "Object Transport Task"

    def add_container(self, source_element=None, base_table=None, display_name=None, delete_residual_objects=0, pk_columns={}, relations=[]):
        container = object_container(self.parent, source_element, base_table, display_name, delete_residual_objects, pk_columns, relations)
        if container.description is not None:
            self.xml_append_node(container.description)
        self.xml_append_node(container)
        return container

    @property
    def accepted_classes(self):
        return ["Transport_Object", "ObjectDataItem"]

    def children(self):
        task_nodes = self.xml_get_children()
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
        # print("add child to transport task")
        # print(object_info_dict)
        base_table = object_info_dict.get("table_name", None)
        display_name = object_info_dict.get("object_display", None)
        pk_columns = object_info_dict.get("pk_columns", None)
        xml_obj = object_container(parent=self.parent, base_table=base_table, display_name=display_name, pk_columns=pk_columns)
        return xml_obj

