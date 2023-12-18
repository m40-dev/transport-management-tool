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

        editor_bg_color = self.ProgramConfiguration.getColor("BaseColor")
        text_color = self.ProgramConfiguration.getColor("TextColor")
        attribute_color = self.ProgramConfiguration.getColor("AltTextColor")
        tag_color = self.ProgramConfiguration.getColor("AltTextColor2")
        description_color = self.ProgramConfiguration.getColor("DescriptionTextColor")

        #Configure colors by their roles
        lexer.setColor(text_color, QsciLexerSQL.Default)
        lexer.setColor(tag_color, QsciLexerSQL.Keyword)
        lexer.setColor(attribute_color, QsciLexerSQL.SingleQuotedString)
        lexer.setColor(description_color, QsciLexerSQL.Comment)

        lexer.setFont(self.font)
        lexer.setDefaultPaper(editor_bg_color)
        lexer.setPaper(editor_bg_color)
        self.setLexer(lexer)