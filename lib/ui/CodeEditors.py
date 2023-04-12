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

        self.light_mode = True

        # AutoIndentation
        self.setAutoIndent(True)
        self.setIndentationGuides(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationWidth(4)
        self.setMarginLineNumbers(1, True)
        self.setMarginWidth(1, 25)
        self.setMarginWidth(0, 0)
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)

        lexer = QsciLexerXML()
        self.setLexer(lexer)

        #line color
        self.setCaretLineVisible(True)
        

        self.reconfigure_editor(lexer)
        self.show()
        self.text_to_find = ""

    def reconfigure_editor(self, lexer):
        editor_bg_color = QColor("#fff")
        editor_text_color = QColor("#333")
        caret_bg_color = QColor("#eee")

        
        if not self.light_mode:
            editor_bg_color = QColor("#1e1f1c")
            editor_text_color = QColor("#eee")
            caret_bg_color = QColor("#555")
            lexer.setColor(editor_text_color)

        lexer.setFont(self.font)
        lexer.setDefaultPaper(editor_bg_color)
        lexer.setPaper(editor_bg_color)

        self.setMarginsBackgroundColor(editor_bg_color)
        self.setMarginsForegroundColor(editor_text_color)
        self.setCaretLineBackgroundColor(caret_bg_color)



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