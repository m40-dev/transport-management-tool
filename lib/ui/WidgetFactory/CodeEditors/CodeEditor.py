from PyQt6.Qsci import QsciScintilla, QsciLexerXML, QsciAPIs, QsciLexerSQL, QsciLexer
from PyQt6.QtGui import QColor, QFont


class BaseCodeEditor(QsciScintilla):
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
        
        self.show()
        self.text_to_find = ""

        self.SendScintilla(QsciScintilla.SCI_SETMULTIPLESELECTION, True)
        self.SendScintilla(QsciScintilla.SCI_SETMULTIPASTE, 1)
        self.SendScintilla(QsciScintilla.SCI_SETADDITIONALSELECTIONTYPING, True)
        self.SendScintilla(QsciScintilla.SCI_SETINDENTATIONGUIDES, QsciScintilla.SC_IV_REAL);
        self.SendScintilla(QsciScintilla.SCI_SETTABWIDTH, 4)
        self.setFolding(QsciScintilla.FoldStyle.PlainFoldStyle)
        self.SCN_MODIFIED = self.modify

        self.reconfigure_editor(lexer)

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
        
        self.SendScintilla(QsciScintilla.SCI_SETFOLDMARGINHICOLOUR, True, editor_bg_color)
        self.SendScintilla(QsciScintilla.SCI_SETFOLDMARGINCOLOUR, True, editor_bg_color)


    def find_text(self, text):
        if text == self.text_to_find:
            return self.findNext()
        
        self.text_to_find = text

        current_cursor_pos = self.getCursorPosition()
        result = self.findFirst(text, False, False, False, True, True, current_cursor_pos[0], 0, True)
        if not result:
            self.findFirst(text, False, False, False, True, True, 0, 0, True)


    def set_fold(self, prev, line, fold, full):
        if (prev[0] >= 0):
            fmax = max(fold, prev[1])
            for iter in range(prev[0], line + 1):
                self.SendScintilla(self.SCI_SETFOLDLEVEL, iter,
                    fmax | (0, self.SC_FOLDLEVELHEADERFLAG)[iter + 1 < full])

    def line_empty(self, line):
        return self.SendScintilla(self.SCI_GETLINEENDPOSITION, line) \
            <= self.SendScintilla(self.SCI_GETLINEINDENTPOSITION, line)

    def modify(self, position, modificationType, text, length, linesAdded,
            line, foldLevelNow, foldLevelPrev, token, annotationLinesAdded):
        full = self.SC_MOD_INSERTTEXT | self.SC_MOD_DELETETEXT
        if (~modificationType & full == full):
            return
        prev = [-1, 0]
        full = self.SendScintilla(self.SCI_GETLINECOUNT)
        lbgn = self.SendScintilla(self.SCI_LINEFROMPOSITION, position)
        lend = self.SendScintilla(self.SCI_LINEFROMPOSITION, position + length)
        for iter in range(max(lbgn - 1, 0), -1, -1):
            if ((iter == 0) or not self.line_empty(iter)):
                lbgn = iter
                break
        for iter in range(min(lend + 1, full), full + 1):
            if ((iter == full) or not self.line_empty(iter)):
                lend = min(iter + 1, full)
                break
        for iter in range(lbgn, lend):
            if (self.line_empty(iter)):
                if (prev[0] == -1):
                    prev[0] = iter
            else:
                fold = self.SendScintilla(self.SCI_GETLINEINDENTATION, iter)
                fold //= self.SendScintilla(self.SCI_GETTABWIDTH)
                self.set_fold(prev, iter - 1, fold, full)
                self.set_fold([iter, fold], iter, fold, full)
                prev = [-1, fold]
        self.set_fold(prev, lend - 1, 0, full)
