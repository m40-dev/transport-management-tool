from PyQt6.Qsci import QsciScintilla, QsciLexerXML, QsciAPIs, QsciLexerSQL, QsciLexer
from PyQt6.QtGui import QColor, QFont


class code_editor(QsciScintilla):
    def __init__(self, parent):
        self.parent = parent
        QsciScintilla.__init__(self, parent)
        #font
        self.font = QFont()
        self.font.setFamily('Consolas')
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        # self.setFont(font)

        self.setMarginsFont(self.font)

        # AutoIndentation
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, 25)
        self.setMarginWidth(0, 0)
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)

        self.editor_bg = QColor("#fff")

        self.setMarginsBackgroundColor(self.editor_bg)

        lexer = QsciLexerXML()
        self.setLexer(lexer)

        #line color
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#eee"))

        self.reconfigure_editor(lexer)
        self.show()
        self.text_to_find = ""

    def reconfigure_editor(self, lexer):
        lexer.setFont(self.font)
        lexer.setDefaultPaper(self.editor_bg)
        lexer.setPaper(self.editor_bg)


    def find_text(self, text):
        if text == self.text_to_find:
            return self.findNext()
        
        self.text_to_find = text

        current_cursor_pos = self.getCursorPosition()
        result = self.findFirst(text, False, False, False, True, True, current_cursor_pos[0], 0, True)
        if not result:
            self.findFirst(text, False, False, False, True, True, 0, 0, True)


class xml_editor(code_editor):
    def __init__(self, parent):
        self.parent = parent
        code_editor.__init__(self, parent)

        

class sql_editor(code_editor):
    def __init__(self, parent):
        self.parent = parent
        code_editor.__init__(self, parent)

        lexer = QsciLexerSQL()
        self.setLexer(lexer)
        self.reconfigure_editor(lexer)