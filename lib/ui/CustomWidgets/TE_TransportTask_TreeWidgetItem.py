from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem
from lib.xml.transport_task import transport_task


class TE_TransportTask_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_TransportTask_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

        self.refresh()
    
    @property
    def display_name(self):
        display = "Transport Task Without Display"
        if isinstance(self.object_data, transport_task):
            display = f"{self.object_data.task_display} - ({self.object_data.task_class})"
        return display