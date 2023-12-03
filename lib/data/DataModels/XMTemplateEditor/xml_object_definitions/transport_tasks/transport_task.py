from ..transport_template_custom_object import transport_template_custom_object


class transport_task(transport_template_custom_object):
    
    def __init__(self, parent, object_class="VI.Transport.ObjectTransport, VI.Transport", source_element=None):
        super(transport_task, self).__init__(parent=parent, node_class="Task", source_element=source_element, xml_object_class=object_class)

        """ Task Node setup"""
        if source_element is not None:
            self.data = source_element
        else:
            self.data.attrib["Class"] = object_class
            self.data.attrib["Display"] = "Generic Transport Template Task"

