from PyQt6.Qsci import QsciLexerSQL
from .CodeEditor import BaseCodeEditor

        
class sql_editor(BaseCodeEditor):
    def __init__(self, parent):
        self.parent = parent
        BaseCodeEditor.__init__(self, parent)

        lexer = QsciLexerSQL()
        self.setLexer(lexer)
        self.reconfigure_editor(lexer)