from lib.data.DataModels.XMTemplateEditor.xml_object_definitions.transport_template_custom_object import transport_template_custom_object

class object_reference(transport_template_custom_object):
    def __init__(self, parent, parameter_name="PK", parameter_value="", source_element=None, display_name=None):
        
        super(object_reference, self).__init__(
            parent=parent, 
            node_class="Parameter", 
            source_element=source_element, 
            xml_object_class="Table_Object_Reference")

        """ Container Node setup"""
        if source_element is None:
            self.data.attrib["Name"] = parameter_name
            if display_name:
                self.data.attrib["Display"] = display_name
            self.data.text = str(parameter_value)
    
    @property
    def accepted_classes(self):
        return ["Table_Object_Reference", "ObjectDataItem"]

    @property
    def accepted_tables(self):
        return [self.table_name]

    @property
    def query_dict(self):
        return {self.key_column: self.data.text}

    