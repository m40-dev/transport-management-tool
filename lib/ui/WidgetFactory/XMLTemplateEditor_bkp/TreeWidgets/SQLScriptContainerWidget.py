from PyQt6.QtCore import Qt
from . import TemplateEditorTreeWidgetItem


class TE_SQLScriptContainer_TreeWidgetItem(TemplateEditorTreeWidgetItem):
    def __init__(self, XMLTemplateEditor, application, object_data, xml_object=None):
        super(TE_SQLScriptContainer_TreeWidgetItem, self).__init__(XMLTemplateEditor=XMLTemplateEditor, application=application, object_data=object_data, xml_object=xml_object)

        self.setFlags(Qt.ItemFlag.ItemIsDragEnabled | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        
        if object_data is None and xml_object is not None:
            self.load_container_from_xml()
        self.refresh()

    def load_container_from_xml(self):
        self.setText(0, self.display_name)

    @property
    def display_name(self):
        if self.xml_object is not None:
            script_type = self.xml_object.get_attribute("Name")
            return script_type

    @property
    def script(self):
        if self.xml_object:
            return self.xml_object.text
        return ""
    
    def set_script(self, script_content):
        if self.xml_object:
            byte_data = bytes(script_content, 'utf-8')
            byte_data = byte_data.replace(b'\r\n', b'\n')
            self.xml_object.set_text(byte_data.decode('utf-8'))
