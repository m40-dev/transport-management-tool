from PyQt6 import QtCore, QtGui, QtWidgets
from lib.ui.WidgetFactory.DialogScreens.CustomDialogWindow import CustomDialogWindow
from lib.ui.WidgetFactory.DialogScreens.MessageBox import MsgBox
from datetime import datetime
import calendar

class DatePickerDialog(CustomDialogWindow):

    def __init__(self, application):
        # super(EncryptionKeyDialog, self).__init__(flags=QtCore.Qt.WindowType.Dialog, parent=application)
        super(DatePickerDialog, self).__init__(application=application, restore_window_state=False)

        self.selected_date = None
        self.setMinimumSize(350, 350)

        self.setupUi()

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)

    def setCurrentDate(self, date):
        self.calendarWidget.setSelectedDate(date)
        self.onSelectionChange()

    def onSelectionChange(self):
        self.pageSelectionChanged(self.calendarWidget.yearShown(), self.calendarWidget.monthShown())

    def selectedDate(self):
        return self.calendarWidget.selectedDate()

    def pageSelectionChanged(self, current_year, current_month):
        month_index = self.monthSelectionComboBox.findData(current_month)
        self.monthSelectionComboBox.setCurrentIndex(month_index)
        year_index = self.yearSelectionComboBox.findData(current_year)
        self.yearSelectionComboBox.setCurrentIndex(year_index)

    def dateSelectionChanged(self, selected_index):
        month_id = self.monthSelectionComboBox.itemData(self.monthSelectionComboBox.currentIndex())
        year_id = self.yearSelectionComboBox.itemData(self.yearSelectionComboBox.currentIndex())
        self.calendarWidget.setCurrentPage(year_id, month_id)

    # def yearSelectionChanged(self, year_index):
    #     month_id = self.monthSelectionComboBox.itemData(self.monthSelectionComboBox.currentIndex())
    #     year_id = self.yearSelectionComboBox.itemData(year_index)
    #     self.calendarWidget.setCurrentPage(year_id, month_id)

    def setupUi(self):
        # basic setup for the calendar widget
        self.calendarWidget = QtWidgets.QCalendarWidget(self)
        self.calendarWidget.setNavigationBarVisible(False)

        # replacement widgets for the navigation bar
        self.prevPage = QtWidgets.QToolButton(self)
        self.nextPage = QtWidgets.QToolButton(self)
        self.monthSelectionComboBox = QtWidgets.QComboBox(self)
        self.yearSelectionComboBox = QtWidgets.QComboBox(self)
        self.showToday = QtWidgets.QPushButton(self)
        self.showToday.setText("Select Today")

        for i in range(datetime.today().year - 20, datetime.today().year + 20):
            self.yearSelectionComboBox.addItem(str(i), i)
            i += 1
        
        for month_name, month_id in MonthSelection.items():
            self.monthSelectionComboBox.addItem(month_name, month_id)

        # configure signals
        self.prevPage.clicked.connect(self.calendarWidget.showPreviousMonth)
        self.nextPage.clicked.connect(self.calendarWidget.showNextMonth)
        self.monthSelectionComboBox.currentIndexChanged.connect(self.dateSelectionChanged)
        self.yearSelectionComboBox.currentIndexChanged.connect(self.dateSelectionChanged)
        self.showToday.clicked.connect(lambda: self.setCurrentDate(datetime.today()))
        self.calendarWidget.currentPageChanged.connect(self.pageSelectionChanged)
        self.calendarWidget.selectionChanged.connect(self.onSelectionChange)


        #configure icons
        arrow_left_icon = self.ProgramConfiguration.getIcon("ArrowLeft_Borderless")
        if arrow_left_icon:
            self.prevPage.setToolTip("<i>Previous Page</i>")
            self.prevPage.setIcon(arrow_left_icon)
            self.prevPage.setIconSize(QtCore.QSize(20, 20))
            self.prevPage.setProperty("Widget", "CustomToolButton")

        arrow_right_icon = self.ProgramConfiguration.getIcon("ArrowRight_Borderless")
        if arrow_right_icon:
            self.nextPage.setToolTip("<i>Previous Page</i>")
            self.nextPage.setIcon(arrow_right_icon)
            self.nextPage.setIconSize(QtCore.QSize(20, 20))
            self.nextPage.setProperty("Widget", "CustomToolButton")

        #layout configuration
        self.form_layout.addWidget(self.prevPage, 0, 0, 1, 1)
        self.form_layout.addWidget(self.monthSelectionComboBox, 0, 1, 1, 1)
        self.form_layout.addWidget(self.yearSelectionComboBox, 0, 2, 1, 1)
        self.form_layout.addWidget(self.nextPage, 0, 3, 1, 1)
        self.form_layout.addWidget(self.calendarWidget, 1,0,1,4)
        self.form_layout.addWidget(self.showToday, 2, 0, 1, 2)
        self.form_layout.setRowStretch(1, 2)



MonthSelection = {month_name: month_number for month_number, month_name in enumerate(calendar.month_name) if month_number != 0}