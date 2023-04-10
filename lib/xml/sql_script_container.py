from lxml import etree
from lib.xml.transport_template_custom_object import transport_template_custom_object
from lib.xml.object_parameter import object_parameter
import numbers
import xmltodict
            
class sql_script_container(transport_template_custom_object):
    def __init__(self, application, source_element=None, script_type="CommonSQL"):
        super(sql_script_container, self).__init__(application=application, node_class="Parameter", source_element=source_element)

        """ Main Container Node setup"""
        if source_element is None and script_type:
            self.data.attrib['Name'] = script_type

    @property
    def script_type(self):
        return self.get_attribute("Name")

    


