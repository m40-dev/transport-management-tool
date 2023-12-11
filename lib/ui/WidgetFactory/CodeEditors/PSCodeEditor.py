from PyQt6.Qsci import QsciLexerPOV
from .CodeEditor import BaseCodeEditor

        
class ps_editor(BaseCodeEditor):
    def __init__(self, parent):
        BaseCodeEditor.__init__(self, parent)

        self.lexer = QsciLexerPOV()
        self.setLexer(self.lexer)
        self.reconfigure_editor()