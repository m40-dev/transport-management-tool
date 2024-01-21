from .CodeEditor import BaseCodeEditor
from PyQt6.Qsci import QsciLexerXML

class xml_editor(BaseCodeEditor):
    def __init__(self, parent):
        BaseCodeEditor.__init__(self, parent)

        self.lexer = QsciLexerXML()
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
        lexer.setColor(text_color, QsciLexerXML.Default)
        lexer.setColor(attribute_color, QsciLexerXML.Attribute)
        lexer.setColor(tag_color, QsciLexerXML.Tag)
        lexer.setColor(description_color, QsciLexerXML.HTMLComment)
        lexer.setColor(string_color, QsciLexerXML.HTMLDoubleQuotedString)

        lexer.setFont(self.font)
        lexer.setDefaultPaper(editor_bg_color)
        lexer.setPaper(editor_bg_color)
        self.setLexer(lexer)