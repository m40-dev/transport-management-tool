from lxml import etree
from .transport_task import transport_task
from .task_containers.object_reference import object_reference
from ..object_parameter import object_parameter

class shell_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.DPR.ShellTransport, VI.Transport.DPR", source_element=None):
        super(shell_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        if source_element is None:
            self.data.attrib["Display"] = "Synchronization Project Transport"
            shells = object_parameter(self.parent, "Shells")
            self.xml_append_node(shells)

    def children(self):
        parent_node = self.xml_get_parameter("Shells")
        child_entries = self.xml_get_children(parent_element=parent_node)
        child_objects = []
        for xml_entry in child_entries:
            if not isinstance(xml_entry, etree._Comment) and isinstance(xml_entry, etree._Element):
                param_name = xml_entry.attrib.get("Name", None)
                xml_obj = None
                if param_name == "PK":
                    xml_obj = object_reference(self.parent, param_name, xml_entry.text, xml_entry)
                    xml_obj.table_name = self.table_name
                if xml_obj:
                    child_objects.append(xml_obj)
        return child_objects

    def xml_add_child_node(self, object_info_dict, row=-1):
        # print("add child to transport task")
        # print(object_info_dict)
        display_name = object_info_dict.get("object_display", None)
        pk_columns = object_info_dict.get("pk_columns", None)
        object_uid = ""
        if pk_columns:
            object_uid = list(pk_columns.values())[0]

        xml_obj = object_reference(
            parent = self.parent,
            display_name = display_name,
            parameter_value = object_uid)
        return xml_obj

    @property
    def table_name(self):
        return "DPRShell"

    @property
    def accepted_tables(self):
        # define what table is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all tables 
        return [self.table_name]

    @property
    def accepted_classes(self):
        # define what class is acceptable for the defined custom object
        # this list will be processed when new element is being added/dropped on the XMLDataItem that carries the specified XML custom object
        # empty list accepts all objects 
        return ["Table_Object_Reference", "ObjectDataItem"]

