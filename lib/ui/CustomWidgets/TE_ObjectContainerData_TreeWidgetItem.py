from PyQt6.QtCore import Qt
from lib.ui.CustomWidgets.TemplateEditorTreeWidgetItem import TemplateEditorTreeWidgetItem


class TE_ObjectContainerData_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, application, object_data, xml_object=None, source_widget=None, table_name=None
    
    ):
        super(TE_ObjectContainerData_TreeWidgetItem, self).__init__(application=application, object_data=object_data, xml_object=xml_object, source_widget=source_widget, table_name=table_name)
        self.setFlags(Qt.ItemFlag.NoItemFlags)
        self.refresh()