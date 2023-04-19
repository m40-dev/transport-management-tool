from .CodeEditor import BaseCodeEditor

class xml_editor(BaseCodeEditor):
    def __init__(self, parent):
        self.parent = parent
        BaseCodeEditor.__init__(self, parent)