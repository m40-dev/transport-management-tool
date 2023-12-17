from PyQt6.QtGui import QPalette, QBrush, QColor
from PyQt6.QtCore import Qt



class ApplicationTheme(QPalette):
    """ xxxxxxxxxxx """

    def __init__(self, ProgramConfiguration):
        QPalette.__init__(self)
        self.ProgramConfiguration = ProgramConfiguration
        self._style_sheet = ""
        self.configurePalette()

    def styleSheet(self):
        # read default stylesheet file
        style_sheet = self.readStyleSheet()
        if style_sheet is None:
            return ""
        
        self.configurePalette()
        # parse stylesheet
        style_sheet = self.parseStyleSheet(style_sheet)

        # save parsed stylesheet until next reload
        self._style_sheet = style_sheet

        # return parsed stylesheet file
        return style_sheet
    
    def parseStyleSheet(self, style_sheet):
        for theme_key, key_configuration in self.ProgramConfiguration.getConfigurationParameterValues("Appearance").items():
            color = self.ProgramConfiguration.getColorFromRGBAString(str(key_configuration))
            if color.isValid():
                style_sheet = style_sheet.replace(f"@{theme_key}", str(key_configuration))
        return style_sheet

    @property
    def style_sheet(self):
        if len(self._style_sheet):
            return self._style_sheet

        # if there is no cached property, try to reload the stylesheet and return that
        return self.styleSheet()
    
    def readStyleSheet(self):
        style = None
        try:
            f = open("./Application.qss")
            style = f.read()
            f.close()
        except FileNotFoundError:
            pass
        return style

    def configurePalette(self):
        brush = QBrush(self.ProgramConfiguration.getColor("BaseColor"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, brush)
        

        brush = QBrush(self.ProgramConfiguration.getColor("AlternativeBaseColor"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush)

        brush = QBrush(self.ProgramConfiguration.getColor("DarkerBaseColor"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.All, QPalette.ColorRole.Dark, brush)
        
        brush = QBrush(self.ProgramConfiguration.getColor("HighlightColor"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, brush)
        
        text_color = self.ProgramConfiguration.getColor("TextColor")
        brush = QBrush(text_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        
        text_color.setAlphaF(0.7)
        brush = QBrush(text_color)
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush)
        

        brush = QBrush(self.ProgramConfiguration.getColor("HighlightedText"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, brush)
        
        brush = QBrush(self.ProgramConfiguration.getColor("InactiveObjectColor"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, brush)
        

        