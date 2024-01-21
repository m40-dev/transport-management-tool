from PyQt6.Qsci import QsciLexerSQL
from .CodeEditor import BaseCodeEditor

        
class sql_editor(BaseCodeEditor):
    def __init__(self, parent):
        BaseCodeEditor.__init__(self, parent)

        self.lexer = QsciLexerSQL()
        self.setLexer(self.lexer)
        self.reconfigure_editor()

    def reconfigure_lexer(self):
        lexer = self.lexer

        editor_bg_color = self.ProgramConfiguration.getColor("CodeEditBGColor")
        text_color = self.ProgramConfiguration.getColor("CodeEditTextNormal")

        attribute_color = self.ProgramConfiguration.getColor("CodeEditTextKeyword1")
        tag_color = self.ProgramConfiguration.getColor("CodeEditTextKeyword2")
        string_color = self.ProgramConfiguration.getColor("CodeEditTextKeyword3")

        description_color = self.ProgramConfiguration.getColor("CodeEditTextComment")

        #Configure colors by their roles
        lexer.setColor(text_color, QsciLexerSQL.Default)
        lexer.setColor(attribute_color, QsciLexerSQL.Keyword)
        lexer.setColor(tag_color, QsciLexerSQL.KeywordSet5)
        lexer.setColor(tag_color, QsciLexerSQL.KeywordSet6)
        lexer.setColor(tag_color, QsciLexerSQL.KeywordSet7)
        lexer.setColor(tag_color, QsciLexerSQL.KeywordSet8)
        
        lexer.setColor(string_color, QsciLexerSQL.SingleQuotedString)
        lexer.setColor(string_color, QsciLexerSQL.DoubleQuotedString)

        lexer.setColor(description_color, QsciLexerSQL.Comment)

        lexer.setFont(self.font)
        lexer.setDefaultPaper(editor_bg_color)
        lexer.setPaper(editor_bg_color)
        self.setLexer(lexer)