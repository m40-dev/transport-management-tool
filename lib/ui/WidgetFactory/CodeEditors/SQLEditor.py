from PyQt6.Qsci import QsciLexerSQL
from .CodeEditor import BaseCodeEditor

        
class sql_editor(BaseCodeEditor):
    def __init__(self, parent):
        self.parent = parent
        BaseCodeEditor.__init__(self, parent)

        self.lexer = QsciLexerSQL()
        self.setLexer(self.lexer)
        self.reconfigure_editor()