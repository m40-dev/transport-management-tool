from .transport_template_custom_object import transport_template_custom_object


class object_parameter(transport_template_custom_object):
    def __init__(self, parent, parameter_name, parameter_value="", source_element=None):
        super(object_parameter, self).__init__(parent=parent, node_class="Parameter", source_element=source_element)
        self._parent = parent

        """ Container Node setup"""
        if source_element is None:
            self.data.attrib["Name"] = parameter_name
            self.data.text = str(parameter_value)
