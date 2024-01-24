
from PyQt6 import QtWidgets, QtCore

from .ConfigurationSectionTreeWidgetItem import ConfigurationSectionTreeWidgetItem
from lib.ui.WidgetFactory import MsgBox

class SettingsWidget(QtWidgets.QWidget):
    configurationReloaded = QtCore.pyqtSignal()

    def __init__(self, application):
        super().__init__()
        self.application = application
        self.ProgramConfiguration = self.application.ProgramConfiguration
        self.current_section = None
        self.setupUi()
        self.loadConfigurationData()

        self.ConfigurationSectionTreeWidget.itemClicked.connect(self.onSectionChanged)
        self.configurationReloaded.connect(lambda current=self.current_section: self.onSectionChanged(self.current_section))
        # self.animate()

    def refresh_ui(self):
        self.setStyleSheet(self.ProgramConfiguration.styleSheet())
        self.ConfigurationSectionTreeWidget.setStyleSheet(self.styleSheet())

    def onSectionChanged(self, source_item):
        if not source_item:
            return False
        # for x in range(self.ConfigurationSectionTabWidget.count()):
        #     self.ConfigurationSectionTabWidget.removeTab(0)
        self.current_section = source_item
        editor_widget = source_item.getSectionEditorWidget()

        if self.ConfigurationSectionTabWidget.indexOf(editor_widget) < 0:
            self.ConfigurationSectionTabWidget.addTab(editor_widget, source_item.SectionName)
        self.ConfigurationSectionTabWidget.setCurrentWidget(editor_widget)

    def setupUi(self):
        # Widget Layout Configuration
        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.setObjectName("SettingsWidget")

        # Configuration sections navigation
        self.ConfigurationSectionTreeWidget = QtWidgets.QTreeWidget()
        self.ConfigurationSectionTreeWidget.setHeaderLabels(["Program Configuration Sections"])
        self.ConfigurationSectionTreeWidget.setProperty("SettingsWidget", "ConfigurationSectionsTreeView")
        self.ConfigurationSectionTreeWidget.header().setProperty("SettingsWidget", "ConfigurationSectionsTreeView")
        self.ConfigurationSectionTreeWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.ConfigurationSectionTreeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.ConfigurationSectionTreeWidget.setColumnCount(1)
        # Configuration section viewport
        # Configuration Toolbox
        toolbox_layout = QtWidgets.QHBoxLayout()
        toolbox_layout.setContentsMargins(0, 0, 0, 0)
        toolbox_layout.setSpacing(2)

        self.ConfigurationSearch = QtWidgets.QLineEdit()
        self.ConfigurationSearch.setPlaceholderText("Search for configuration...")
        self.ConfigurationApplyButton = QtWidgets.QToolButton()
        self.ConfigurationApplyButton.setText("Save Configuration")
        self.ConfigurationApplyButton.clicked.connect(self.saveConfigurationData)

        toolbox_layout.addWidget(self.ConfigurationSearch)
        toolbox_layout.addWidget(self.ConfigurationApplyButton)

        self.ConfigurationSectionTabWidget = QtWidgets.QTabWidget()
        self.ConfigurationSectionTabWidget.tabBar().setVisible(False)

        configuration_widget = QtWidgets.QWidget()
        configuration_widget_layout = QtWidgets.QVBoxLayout(configuration_widget)
        configuration_widget_layout.setContentsMargins(0, 0, 0, 0)
        configuration_widget_layout.setSpacing(2)
        configuration_widget_layout.addLayout(toolbox_layout)
        configuration_widget_layout.addWidget(self.ConfigurationSectionTabWidget)

        # Add main widgets into splitter layout
        self.ConfigurationViewSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.ConfigurationViewSplitter.addWidget(self.ConfigurationSectionTreeWidget)
        self.ConfigurationViewSplitter.addWidget(configuration_widget)

        # Insert Main Layout Widgets
        self.layout.addWidget(self.ConfigurationViewSplitter, 0, 0)

        # Configure workspace proportions
        self.ConfigurationViewSplitter.setSizes(
            [round(self.application.width()*0.2), round(self.application.width()*0.8)])

    def loadConfigurationData(self):
        configuration_items = []
        for section, section_data in self.ProgramConfiguration.ProgramConfiguration.items():
            if section_data.get("IsEditable", True) is False:
                continue

            configuration_section = ConfigurationSectionTreeWidgetItem(
                parent=None,
                application=self.application,
                settings_module=self,
                section_name=section,
                section_data=section_data)
            configuration_items.append(configuration_section)

        self.ConfigurationSectionTreeWidget.addTopLevelItems(configuration_items)

    def saveConfigurationData(self):
        if self.ProgramConfiguration.saveConfiguration():
            MsgBox(
            application=self.application,
            window_mode=MsgBox.INFO,
            window_title="Configuration Saved",
            message="Program Configuration saved."
            )



