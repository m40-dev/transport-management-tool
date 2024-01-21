from PyQt6.Qsci import QsciLexerPOV
from .CodeEditor import BaseCodeEditor

        
class ps_editor(BaseCodeEditor):
    def __init__(self, parent):
        BaseCodeEditor.__init__(self, parent)

        self.lexer = QsciLexerPOV()
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
        lexer.setColor(text_color, QsciLexerPOV.Default)

        lexer.setColor(attribute_color, QsciLexerPOV.KeywordSet6)
        lexer.setColor(attribute_color, QsciLexerPOV.KeywordSet7)
        lexer.setColor(attribute_color, QsciLexerPOV.KeywordSet8)

        lexer.setColor(tag_color, QsciLexerPOV.BadDirective)
        lexer.setColor(tag_color, QsciLexerPOV.Directive)
        lexer.setColor(tag_color, QsciLexerPOV.Identifier)
        lexer.setColor(tag_color, QsciLexerPOV.Operator)
        lexer.setColor(tag_color, QsciLexerPOV.ObjectsCSGAppearance)
        lexer.setColor(tag_color, QsciLexerPOV.Number)
        lexer.setColor(tag_color, QsciLexerPOV.PredefinedFunctions)
        lexer.setColor(tag_color, QsciLexerPOV.PredefinedIdentifiers)
        lexer.setColor(tag_color, QsciLexerPOV.TypesModifiersItems)

        lexer.setColor(description_color, QsciLexerPOV.CommentLine)
        lexer.setColor(description_color, QsciLexerPOV.Comment)
        lexer.setColor(string_color, QsciLexerPOV.String)

        lexer.setFont(self.font)
        lexer.setDefaultPaper(editor_bg_color)
        lexer.setPaper(editor_bg_color)
        self.setLexer(lexer)