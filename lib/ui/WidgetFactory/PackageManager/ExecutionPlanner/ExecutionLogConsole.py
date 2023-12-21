from PyQt6 import QtCore, QtGui, QtWidgets

class ExecutionLogConsole(QtWidgets.QTextEdit):

    def __init__(self, parent, application):
        super(ExecutionLogConsole, self).__init__(parent=parent)
        
        self.parent = parent
        self.application = application
        self.ProgramConfiguration = application.ProgramConfiguration        

        self.setProperty("ExecutionPlanner", "ConsoleReader")

        self.setAcceptRichText(True)
        self.setWordWrapMode(QtGui.QTextOption.WrapMode.WordWrap)
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.WidgetWidth)
        self.setLineWrapColumnOrWidth(self.width())

        self.defaultBlockFormat = self.textCursor().blockFormat()
        self.defaultBlockFormat.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.defaultBlockFormat.setTopMargin(0)
        self.defaultBlockFormat.setBottomMargin(0)
        self.defaultBlockFormat.setLeftMargin(0)
        self.defaultBlockFormat.setRightMargin(0)

        self.textCursor().setBlockFormat(self.defaultBlockFormat)

        self.setStyleSheet(self.application.styleSheet())
        self.document().setDefaultStyleSheet(self.ProgramConfiguration.styleSheet())

    def appendLogs(self, formatted_message):
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End, QtGui.QTextCursor.MoveMode.MoveAnchor)
        if cursor.blockNumber() > 0:
            cursor.insertBlock(self.defaultBlockFormat)

        cursor.insertHtml(formatted_message)

        # restore cursor location at the end, this effectively scrolls the log view automatically
        self.setTextCursor(cursor)

    def refresh_ui(self):
        self.document().setDefaultStyleSheet(self.ProgramConfiguration.styleSheet())