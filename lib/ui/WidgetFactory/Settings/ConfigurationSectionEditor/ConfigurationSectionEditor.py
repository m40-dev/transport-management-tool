
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from lib.ui.WidgetFactory.DialogScreens.FormEditorDialog import FormEditorObject

class ConfigurationSectionEditor(QtWidgets.QWidget):
    reloadEditor = pyqtSignal()
    
    def __init__(self, application, section_name, section_source):
        super().__init__()

        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration

        self._section_source = section_source
        self._section_name = section_name

        self.editors = {}
        self.setupUi()

    @property
    def section_display_name(self):
        return self._section_source._section_data.get("DisplayName", "")
    
    @property
    def description(self):
        return self._section_source._section_data.get("Description", "")

    @property
    def section_source(self):
        return self._section_source

    def reloadSection(self):
        pass
    
    def setupUi(self):

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setObjectName("MainLayout")
        self.layout.setSpacing(2)
        self.layout.setContentsMargins(2,2,2,2)

        name_label = QtWidgets.QLabel(f"{self.section_display_name}")
        name_label.setProperty("ConfigurationEditor", "SectionLabel")

        description_label = QtWidgets.QLabel(f"<p>{self.description}</p>")
        description_label.setProperty("ConfigurationEditor", "SectionDescription")

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        
        #layout for any dedicated editor widgets
        
        self.scroll_area = QtWidgets.QScrollArea(self)
        
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.area_widget = QtWidgets.QWidget()
        self.scroll_area.setWidget(self.area_widget)

        self.editor_layout = QtWidgets.QGridLayout()
        self.editor_layout.setObjectName("EditorLayout")

        self.area_widget.setLayout(self.editor_layout)
        

        #Add Widgets to the main layout
        self.layout.addWidget(name_label, 0, 0)
        self.layout.addWidget(description_label,1, 0)
        self.layout.addWidget(separator, 2, 0, 1, -1)

        self.layout.addWidget(self.scroll_area, 3, 0, -1, -1)
        # self.layout.addLayout(self.editor_layout, 3, 0, -1, -1)

    def updateConfigurationKey(self, configuration_key, new_value):
        # print(configuration_key, new_value)
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, None)
        
        field_configuration["ConfigurationValue"] = new_value
    
    def getCurrentValue(self, configuration_key):
        field_configuration = self._section_source.ConfigurationParameters.get(configuration_key, {})
        configuration_value = field_configuration.get("ConfigurationValue", None)
        
        if not configuration_value:
            configuration_value = field_configuration.get("DefaultValue", None)
        return configuration_value

    def addToFormLayout(self, layout, column_name, field_configuration, row, column, rowSpan=1, colSpan=1):
        # current_value = self.configuration_item.data(column_name, None)
        current_value = self.getCurrentValue(column_name)
        
        # field_configuration = self.widget_data.get(column_name, None)
        if field_configuration:
            if current_value is None and "DefaultValue" in field_configuration.keys():
                current_value = field_configuration["DefaultValue"]
                # self.configuration_item.setData(column_name, current_value)
            field_description = field_configuration.get("Description", None)

            field_editor = FormEditorObject(
                parent=self,
                application=self.application,
                column_name=column_name,
                column_configuration=field_configuration)

            if field_editor.editor:
                layout.addWidget(field_editor.label, row, column, 1, 1)

                if field_description:
                    description_label = QtWidgets.QLabel(self)
                    description_label.setText(f"<i>{field_description}</i>")
                    description_label.setWordWrap(True)
                    description_label.setProperty("ConfigurationEditor", "PropertyDescription")
                    layout.addWidget(description_label, row + 1, column, 1, 1, Qt.AlignmentFlag.AlignTop)
                    layout.setRowStretch(row + 1, 2)
                    rowSpan += 1

                column += 1
                layout.addWidget(field_editor.editor, row, column, rowSpan, colSpan, Qt.AlignmentFlag.AlignTop)
                
                if field_editor.canMaximize:
                    #Add Maximize button for widgets that could be otherwise too small
                    max_button = QtWidgets.QToolButton(self)
                    max_button.setProperty("ConfigurationEditor", "MaximizePropertyEditor")
                    layout.addWidget(max_button, row, column, alignment=Qt.AlignmentFlag.AlignRight)
                    max_button.clicked.connect(lambda: self.maximizeEditor(field_editor))
                
                # if current_value:
                field_editor.set_editor_data(current_value)

                field_editor.dataChanged.connect(self.updateConfigurationKey)

                field_editor.label.setProperty("ConfigurationEditor", "PropertyLabel")
                field_editor.editor.setProperty("ConfigurationEditor", "PropertyEditor")
            else:
                if field_editor.label:
                    field_editor.label.deleteLater()
                field_editor.label=None
            self.editors[column_name] = field_editor
            return field_editor
        return None
    
    def maximizeEditor(self, editor):
        if editor.canMaximize:
            editor.maximizeEditor()


