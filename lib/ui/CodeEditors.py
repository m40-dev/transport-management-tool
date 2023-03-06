from PyQt6.Qsci import QsciScintilla, QsciLexerXML, QsciAPIs
from PyQt6.QtGui import QColor, QFont


class xml_editor(QsciScintilla):
    def __init__(self, parent):
        self.parent = parent
        QsciScintilla.__init__(self, parent)
        #font
        font = QFont()
        font.setFamily('Consolas')
        font.setFixedPitch(True)
        font.setPointSize(10)
        # self.setFont(font)

        self.setMarginsFont(font)

        # AutoIndentation
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setMarginsBackgroundColor(QColor("#eef"))
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, 25)
        self.setMarginWidth(0, 0)
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)
        self.lexer = QsciLexerXML()
        self.lexer.setFont(font)
        api = QsciAPIs(self.lexer)

        api.prepare()
        #autocomplete
        self.setLexer(self.lexer)
        self.setAutoCompletionThreshold(3)
        #self.setAutoCompletionSource(QsciScintilla.AcsAPIs)
        #bracket match
        #line color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#eee"))
        self.show()

    # def setText(self, newtext):
    #     QsciScintilla.setText(self, newtext)

    def find_text(self, text, start_line=0):
        print("find text", text)

        if not self.findNext():
            current_cursor_pos = self.getCursorPosition()
            result = self.findFirst(text, False, False, False, True, True, start_line, 0, True)
            new_cursor_pos = self.getCursorPosition()

        # if(result and current_cursor_pos[0] == new_cursor_pos[0]):
        #     self.findNext()


