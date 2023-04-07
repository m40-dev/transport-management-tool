from PyQt6.QtWidgets import  QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

TYPE_COLUMN = 1

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
    
    def __lt__(self, other):
        object_type = self.data(TYPE_COLUMN, Qt.ItemDataRole.InitialSortOrderRole)
        other_type = other.data(TYPE_COLUMN, Qt.ItemDataRole.InitialSortOrderRole)

        if object_type == other_type:
            object_text = self.text(0)
            other_text = other.text(0)
            return min(object_text, other_text) > object_text
        return object_type < other_type


class PackageManagerXMLFile(PackageManagerTreeWidgetItem):
    def __init__(self, application, object_data):
        super(PackageManagerXMLFile, self).__init__(application=application, object_data=object_data)

    @property
    def display_name(self):
        return self.object_data.name
    
    @property
    def path(self):
        return self.object_data.as_posix()
    
    @property
    def directory(self):
        return self.object_data.parent
    
class PackageManagerXMLFolder(PackageManagerTreeWidgetItem):
    def __init__(self, application, object_data):
        super(PackageManagerXMLFolder, self).__init__(application=application, object_data=object_data)
        font = QFont()
        font.setBold(True)
        self.setFont(0, font)

    @property
    def display_name(self):
        return self.object_data.name
    
    @property
    def path(self):
        return self.object_data.absolute()
    
    @property
    def parent_directory(self):
        return self.object_data.parent
    
