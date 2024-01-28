from PyQt6 import QtCore, QtGui, QtWidgets
from lib.ui.WidgetFactory.CustomWindowDecorations import WindowTitleDecoration

class Ui_MainWindow(object):
    def __init__(self, application):
        super(Ui_MainWindow).__init__()
        self.application = application
        self.setupUi(application)

    def setupUi(self, MainWindow):

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(2121, 1215)
        # self.MainLayout = QtWidgets.QVBoxLayout(MainWindow)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.WindowDecoration = WindowTitleDecoration(MainWindow, self.application)
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.SideBar_Layout = QtWidgets.QVBoxLayout()
        self.SideBar_Layout.setObjectName("SideBar_Layout")
        self.horizontalLayout.addLayout(self.SideBar_Layout)

        self.MainTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.MainTabWidget.setTabPosition(QtWidgets.QTabWidget.TabPosition.West)
        self.MainTabWidget.setTabShape(QtWidgets.QTabWidget.TabShape.Rounded)
        self.MainTabWidget.setElideMode(QtCore.Qt.TextElideMode.ElideLeft)
        self.MainTabWidget.setDocumentMode(True)
        self.MainTabWidget.setMovable(True)
        self.MainTabWidget.setTabBarAutoHide(True)
        self.MainTabWidget.setObjectName("MainTabWidget")

        self.horizontalLayout.addWidget(self.MainTabWidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        # self.menubar.setGeometry(QtCore.QRect(0, 0, 2121, 22))
        self.menubar.setObjectName("menubar")
        self.menuMenu = QtWidgets.QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        self.menuConnections = QtWidgets.QMenu(self.menubar)
        self.menuConnections.setObjectName("menuConnections")

        # self.menuAbout = QtWidgets.QMenu(self.menubar)
        # self.menuAbout.setObjectName("menuAbout")

        #Execution Planner Menu Configuration
        # self.menuExecutionPlanner = QtWidgets.QMenu(self.menubar)
        # self.menuExecutionPlanner.setObjectName("menuExecutionPlanner")

        action_NewExecutionPlan = QtGui.QAction(MainWindow)
        action_NewExecutionPlan.setObjectName("actionSave_As")
        action_NewExecutionPlan.setText("Add New Execution Plan")
        # action_NewExecutionPlan = self.menuExecutionPlanner.addAction("Add New Execution Plan")
        action_NewExecutionPlan.triggered.connect(MainWindow.addExecutionPlan)

        #Relation Presets Menu Configuration
        self.menuRelationPresets = QtWidgets.QMenu(self.menubar)
        self.menuRelationPresets.setObjectName("menuRelationPresets")

        action_managePresets = self.menuRelationPresets.addAction("Manage Presets")
        action_ExportPresetData = self.menuRelationPresets.addAction("Export Preset Data")
        action_ImportPresetData = self.menuRelationPresets.addAction("Import Preset Data")
        
        #Connect Menu Signals
        action_managePresets.triggered.connect(MainWindow.manageRelationPresets)
        action_ExportPresetData.triggered.connect(MainWindow.exportRelationPresets)
        action_ImportPresetData.triggered.connect(MainWindow.importRelationPresets)

        #add Menu elements to the window decoration
        self.WindowDecoration.setMenuBar(self.menubar)
        

        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.title_bar = self.WindowDecoration

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0)
        MainWindow.setStatusBar(self.statusbar)

        # leave space for the titlebar
        self.gridLayout.setContentsMargins(5, 34, 5, 5)
        self.gridLayout.setSpacing(2)

        # self.MainLayout.addWidget(self.WindowDecoration)
        # self.MainLayout.addWidget(self.centralwidget)
        # self.MainLayout.addWidget(self.statusbar)


        # MainWindow.setStatusBar(self.statusbar)
        self.actionSaveFile = QtGui.QAction(MainWindow)
        self.actionSaveFile.setObjectName("actionSaveFile")
        self.actionConnect_to_database = QtGui.QAction(MainWindow)
        self.actionConnect_to_database.setObjectName("actionConnect_to_database")
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionInfo = QtGui.QAction(MainWindow)
        self.actionInfo.setObjectName("actionInfo")
        # self.actionHelp = QtGui.QAction(MainWindow)
        # self.actionHelp.setObjectName("actionHelp")
        self.actionAdd_DatabaseConnection = QtGui.QAction(MainWindow)
        self.actionAdd_DatabaseConnection.setObjectName("actionAdd_DatabaseConnection")
        self.actionChange_WorkingDirectory = QtGui.QAction(MainWindow)
        self.actionChange_WorkingDirectory.setObjectName("actionChange_WorkingDirectory")
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionOpen_File = QtGui.QAction(MainWindow)
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.actionSave_As = QtGui.QAction(MainWindow)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionNew_Transport_Template = QtGui.QAction(MainWindow)
        self.actionNew_Transport_Template.setObjectName("actionNew_Transport_Template")
        # self.actionNew_TransportDefinition = QtGui.QAction(MainWindow)
        # self.actionNew_TransportDefinition.setObjectName("actionNew_TransportDefinition")
        
        self.menuMenu.addAction(self.actionNew_Transport_Template)
        self.menuMenu.addAction(action_NewExecutionPlan)

        self.menuMenu.addSeparator()

        self.menuMenu.addMenu(self.menuRelationPresets)

        self.menuMenu.addSeparator()

        self.menuMenu.addAction(self.actionOpen_File)
        self.menuMenu.addAction(self.actionSaveFile)
        self.menuMenu.addAction(self.actionSave_As)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionAbout)
        self.menuMenu.addAction(self.actionSettings)
        self.menuMenu.addSeparator()
        self.menuMenu.addAction(self.actionChange_WorkingDirectory)
        
        self.menuConnections.addAction(self.actionAdd_DatabaseConnection)
        self.menuConnections.addSeparator()
        self.menubar.addAction(self.menuMenu.menuAction())
        self.menubar.addAction(self.menuConnections.menuAction())
        # self.menubar.addAction(self.menuExecutionPlanner.menuAction())
        # self.menubar.addAction(self.menuRelationPresets.menuAction())
        # self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        self.MainTabWidget.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuMenu.setTitle(_translate("MainWindow", "Menu"))
        # self.menuAbout.setTitle(_translate("MainWindow", "About"))
        self.menuConnections.setTitle(_translate("MainWindow", "Connections"))
        # self.menuExecutionPlanner.setTitle(_translate("MainWindow", "Execution Planner"))
        self.menuRelationPresets.setTitle(_translate("MainWindow", "Relation Presets Configuration"))
        self.actionSaveFile.setText(_translate("MainWindow", "Save File"))
        self.actionSaveFile.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionConnect_to_database.setText(_translate("MainWindow", "Connect to database"))
        self.actionSettings.setText(_translate("MainWindow", "Settings"))
        self.actionInfo.setText(_translate("MainWindow", "Info"))
        # self.actionHelp.setText(_translate("MainWindow", "Help"))
        self.actionAdd_DatabaseConnection.setText(_translate("MainWindow", "Add Database Connection"))
        self.actionChange_WorkingDirectory.setText(_translate("MainWindow", "Change Working Directory"))
        self.actionAbout.setText(_translate("MainWindow", "About"))
        self.actionOpen_File.setText(_translate("MainWindow", "Open File"))
        self.actionSave_As.setText(_translate("MainWindow", "Save As"))
        self.actionNew_Transport_Template.setText(_translate("MainWindow", "Create New Transport Template"))
        # self.actionNew_TransportDefinition.setText(_translate("MainWindow", "Add New Transport Definition"))
