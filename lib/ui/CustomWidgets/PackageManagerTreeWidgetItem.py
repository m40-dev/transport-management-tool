from PyQt6.QtWidgets import  QTreeWidgetItem
from PyQt6.QtCore import Qt

class PackageManagerTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, application, object_data):
        super(PackageManagerTreeWidgetItem, self).__init__()

        self.application = application
        self.object_data = object_data

        self.refresh()

    def refresh(self):
        self.setText(0, self.display_name)

    @property
    def display_name(self):
        return "Package Manager Object"


class PackageManagerXMLFile(PackageManagerTreeWidgetItem):
    def __init__(self, application, object_data):
        super(PackageManagerXMLFile, self).__init__(application=application, object_data=object_data)

    @property
    def display_name(self):
        return self.object_data.name
    
    @property
    def file_path(self):
        return self.object_data.as_posix()
    
    @property
    def file_directory(self):
        return self.object_data.parent