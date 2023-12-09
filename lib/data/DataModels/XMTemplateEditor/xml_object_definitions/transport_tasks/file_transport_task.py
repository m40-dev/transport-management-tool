from lxml import etree
from .transport_task import transport_task
from .task_containers.object_reference import object_reference
from ..object_parameter import object_parameter

class file_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.FileTransport, VI.Transport", source_element=None):
        super(file_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        self._parent = parent

        if source_element is None:
            self.xml_set_attribute("Display", "File Transport")
        self.remap_XML_nodes()

    def remap_XML_nodes(self, reassign=False):
        xml_files = self.xml_get_parameter("Files")
        self.files = object_parameter(self, "Files", source_element=xml_files)

    def children(self):
        child_entries = self.files.xml_get_children()
        child_entries += self.xml_get_children()

        child_objects = []
        for xml_entry in child_entries:
            if not isinstance(xml_entry, etree._Comment) and isinstance(xml_entry, etree._Element):
                param_name = xml_entry.attrib.get("Name", None)
                xml_obj = None
                if param_name == "PK":
                    xml_obj = object_reference(self, param_name, xml_entry.text, xml_entry)
                    xml_obj.table_name = self.table_name
                    xml_obj.key_column = self.key_column_name
                if xml_obj:
                    child_objects.append(xml_obj)
        return child_objects
    
    def xml_add_child_node(self, object_info_dict, row=-1):
        # print("add child to transport task")
        display_name = object_info_dict.get("object_display", None)
        pk_columns = object_info_dict.get("pk_columns", None)
        object_uid = ""
        if pk_columns:
            object_uid = list(pk_columns.values())[0]

        xml_obj = object_reference(
            parent = self,
            display_name = display_name,
            parameter_value = object_uid)
        
        xml_obj.table_name = self.table_name
        xml_obj.key_column = self.key_column_name
        
        return xml_obj

    @property
    def table_name(self):
        return "QBMFileRevision"

    @property
    def key_column_name(self):
        return "UID_QBMFileRevision"
    
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

    def prepare_export_data(self):
        for custom_object in self.children():
            self.files.xml_append_node(custom_object)

        self.xml_append_node(self.files)

        return self.string