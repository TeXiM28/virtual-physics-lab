from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class DigitalMultimeter(QWidget):
    def __init__(self, name="Вольтметр анодный", unit="В"):
        super().__init__()
        self.name = name
        self.unit = unit
        self.value = 0.0
        self.setMinimumSize(220, 90)
        self.is_dark = True

    def set_theme(self, is_dark):
        self.is_dark = is_dark
        self.update()

    def set_value(self, val):
        self.value = val
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        
        body_color = QColor("#2C3E50") if self.is_dark else QColor("#D3D3D3")
        text_color = QColor("#FFFFFF") if self.is_dark else QColor("#000000")
        
        painter.setBrush(body_color)
        painter.drawRect(5, 5, self.width()-10, self.height()-10)
        
        painter.setBrush(QColor("#1ABC9C"))
        painter.drawRect(15, 25, self.width()-30, 45)
        
        painter.setPen(QPen(text_color, 1))
        painter.setFont(QFont("Arial", 9))
        painter.drawText(15, 18, self.name)
        
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.setFont(QFont("Courier New", 18, QFont.Weight.Bold))
        painter.drawText(25, 55, f"{self.value:.2f} {self.unit}")