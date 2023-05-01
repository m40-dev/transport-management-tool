from PyQt6.QtGui import QPalette, QBrush, QColor
from PyQt6.QtCore import Qt



class Application_Theme(QPalette):
    """ xxxxxxxxxxx """

    def __init__(self):
        QPalette.__init__(self)

        self.highlight_color = QColor(201, 242, 222, 250)

        brush = QBrush(QColor(235, 235, 235))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush)

        brush = QBrush(QColor(155, 155, 155))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.All, QPalette.ColorRole.Dark, brush)

        brush = QBrush(QColor(225, 225, 225))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush)

        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush)
        
        brush = QBrush(QColor(201, 242, 222, 120))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Highlight, brush)
        
        brush = QBrush(QColor(220, 226, 230, 95))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush)

        brush = QBrush(QColor(220, 100, 100, 95))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.HighlightedText, brush)
        
        brush = QBrush(QColor(155, 155, 155))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush)
        
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush)
        
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush)
        
        brush = QBrush(QColor(158, 176, 226, 80))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Highlight, brush)
        
        brush = QBrush(QColor(220, 226, 230, 95))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush)
        
        brush = QBrush(QColor(155, 155, 155))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush)
        
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush)
        
        brush = QBrush(QColor(255, 255, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush)
        
        brush = QBrush(QColor(0, 120, 215))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Highlight, brush)

        brush = QBrush(QColor(220, 226, 230, 95))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        self.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush)

    @property
    def style_sheet(self):
        """ xxxxxx """
        style = None
        try:
            f = open("./Application.qss")
            style = f.read()
            f.close()
        except FileNotFoundError:
            print("stylesheet file not found")
        return style