from .transport_task import transport_task

class sysconfig_transport_task(transport_task):
    
    def __init__(self, parent, object_class="VI.Transport.BufferTransport, VI.Transport", source_element=None):
        super(sysconfig_transport_task, self).__init__(parent=parent, object_class=object_class, source_element=source_element)
        # self._parent = parent

        if source_element is None:
            self.data.attrib["Display"] = "System Configuration Transport"

    @property
    def accepted_classes(self):
        return [None]

    @property
    def accepted_tables(self):
        return [None] 