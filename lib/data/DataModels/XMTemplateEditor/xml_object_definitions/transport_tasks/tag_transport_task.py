from lxml import etree
from .transport_task import transport_task
from .task_containers.object_reference import object_reference
from ..object_parameter import object_parameter
from ..transport_template_custom_object import transport_template_custom_object

class tag_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.TagTransport, VI.Transport", source_element=None):   
        super(tag_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        
        self._option = "Lock Labels on Export"

        if source_element is None:
            self.xml_set_attribute("Display", "Change Label Transport")
        
        self.remap_XML_nodes()
    
    def remap_XML_nodes(self, reassign=False):
        xml_tags = self.xml_get_parameter("Tags")
        self.tags = object_parameter(self, "Tags", source_element=xml_tags)
        
        xml_options = self.xml_get_parameter("Options")
        self.xml_options = object_parameter(self, "Options", source_element=xml_options)

        xml_lock_tags = self.xml_get_parameter("LockTags", self.xml_options.data)
        self.xml_lock_tags = object_parameter(self.xml_options, "LockTags", 0, source_element=xml_lock_tags)

        xml_use_relations = self.xml_get_parameter("UseRelations", self.xml_options.data)
        self.xml_use_relations = object_parameter(self.xml_options, "UseRelations", 1, source_element=xml_use_relations)

    @property
    def table_name(self):
        return "DialogTag"

    @property
    def key_column_name(self):
        return "UID_DialogTag"

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

    @property
    def state(self):
        value = self.lockTags() 
        if value > 0:
            value = 2
        return value
    
    @state.setter
    def state(self, value):
        if value > 0:
            value = 1
        self.setLockTags(value)

    def setLockTags(self, status):
        self.xml_lock_tags.text = str(status)
    
    def lockTags(self):
        if len(self.xml_lock_tags.text.strip()) > 0:
            if self.xml_lock_tags.text.isnumeric():
                return int(self.xml_lock_tags.text)
        return 0

    def children(self):
        child_entries = self.xml_get_children(parent_element=self.data)
        child_entries += self.xml_get_children(parent_element=self.tags.data)
        child_objects = []
        for xml_entry in child_entries:
            if not isinstance(xml_entry, etree._Comment) and isinstance(xml_entry, etree._Element):
                param_name = xml_entry.attrib.get("Name", None)
                xml_obj = None
                if param_name == "PK":
                    xml_obj = object_reference(self.tags, param_name, xml_entry.text, xml_entry)
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
            parent=self,
            display_name = display_name,
            parameter_value = object_uid)
        
        xml_obj.table_name = self.table_name
        xml_obj.key_column = self.key_column_name

        return xml_obj

    def prepare_export_data(self):
        # Fixes xml data structure hierarchy and moves the child nodes into correct sub-container in the task structure. 
        # Collect all object reference elements currently available on the task node and reassign them to correct parent node under the task structure
        # Additionally add task configuration nodes that were deleted by the model operations 

        for tag_element in self.children():
            self.tags.xml_append_node(tag_element)

        self.xml_append_node(self.tags)
        self.xml_append_node(self.xml_options)

        return self.string