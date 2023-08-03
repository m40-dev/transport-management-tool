from .transport_template_custom_object import transport_template_custom_object
            
class sql_script_container(transport_template_custom_object):
    def __init__(self, parent, source_element=None, script_type="CommonSQL"):
        super(sql_script_container, self).__init__(parent=parent, node_class="Parameter", source_element=source_element)

        """ Main Container Node setup"""
        if source_element is None and script_type:
            self.data.attrib['Name'] = script_type

    @property
    def script_type(self):
        return self.xml_get_attribute("Name")

    @property
    def xml_object_class(self):
        return "Transport_SQL_Object"

    @property
    def display(self):
        return self.script_type