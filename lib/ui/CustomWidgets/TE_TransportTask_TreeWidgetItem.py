from PyQt6.QtCore import Qt
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem
from lib.ui.CustomWidgets.TE_SQLScriptContainer_TreeWidgetItem import TE_SQLScriptContainer_TreeWidgetItem
from lib.xml.transport_task import transport_task, sql_script_transport_task


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

class TE_ObjectTransportTask_TreeWidgetItem(TE_TransportTask_TreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_ObjectTransportTask_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)


class TE_SQLTransportTask_TreeWidgetItem(TE_TransportTask_TreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None):
        super(TE_SQLTransportTask_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget)

        self.setCheckState(1, Qt.CheckState.Unchecked)  
        self.setText(1, "Run Before Import")
        self.refresh()


    def handle_data_change(self, column):
        status = int(self.checkState(column) == Qt.CheckState.Checked)
        tree_widget = self.treeWidget()

        self.set_task_option(column, status)

        for element in tree_widget.selectedItems():
            if isinstance(element, TE_SQLTransportTask_TreeWidgetItem) and element != self:
                element.setCheckState(column, self.checkState(status))

    def refresh(self):
        if self.object_data is not None:
            TemplateEditorTreeWidgetItem.refresh(self)

        if isinstance(self.xml_object, sql_script_transport_task):
            if self.xml_object.pre_import == 1:
                self.setCheckState(1, Qt.CheckState.Checked)
            else:
                self.setCheckState(1, Qt.CheckState.Unchecked)

    def set_task_option(self, option, status):
        if self.object_data.task_class == "VI.Transport.SQLTransport, VI.Transport":
            self.setCheckState(option, self.checkState(status))
            if option == 1 and self.xml_object:
                self.xml_object.set_pre_import(status)
    
    def add_script(self, script_type):
        if isinstance(self.xml_object, sql_script_transport_task):
            xml_data = self.xml_object.add_sql_script(script_type)
            script_widget = TE_SQLScriptContainer_TreeWidgetItem(self.application, xml_data, xml_data)
            self.addChild(script_widget)
            return script_widget