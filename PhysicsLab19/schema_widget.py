import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont

class CircuitSchemaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(220)
        self.setFixedHeight(220)
        self.setFixedWidth(780) 
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        
        painter.setBrush(QColor("#261612"))
        painter.setPen(QPen(QColor("#5D4037"), 2))
        painter.drawRect(5, 5, self.width() - 10, self.height() - 10)
        
        painter.setPen(QPen(QColor("#FFFFFF"), 1.5))
        painter.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        
        
        painter.drawText(20, 45, "к выпрямителю")
        painter.drawEllipse(25, 60, 6, 6)
        painter.drawEllipse(25, 140, 6, 6)
        
        
        painter.drawRect(95, 53, 35, 14)
        painter.drawText(107, 45, "R1")
        painter.drawLine(31, 63, 95, 63)  
        painter.drawLine(112, 53, 112, 35) 
        painter.drawLine(112, 35, 150, 35) 
        
        
        painter.drawText(155, 75, "C")
        painter.drawLine(150, 35, 150, 50)
        for i in range(4):
            painter.drawArc(142, 50 + i*14, 16, 14, -90*16, 180*16)
        painter.drawLine(150, 106, 150, 143) 
        
        
        painter.drawLine(31, 143, 55, 143)
        painter.drawLine(55, 143, 65, 133) 
        painter.drawText(52, 125, "SA1")
        painter.drawLine(70, 143, 85, 143)
        
        painter.drawEllipse(85, 133, 20, 20) 
        painter.drawText(92, 146, "A")
        painter.drawLine(105, 143, 150, 143)
        
       
        painter.drawEllipse(230, 60, 45, 45)
        painter.drawLine(252, 68, 252, 88) 
        painter.drawArc(245, 82, 14, 12, 0, 180*16) 
        
        
        painter.drawLine(150, 143, 248, 143)
        painter.drawLine(248, 143, 248, 94) 
        
        
        painter.drawLine(256, 94, 256, 115)
        painter.drawLine(256, 115, 385, 115) 
        
        painter.drawText(200, 168, "Тр. 1")
        painter.drawLine(225, 152, 265, 152) 
        painter.drawLine(225, 157, 265, 157) 
        painter.drawLine(225, 162, 265, 162) 
        
        painter.drawLine(248, 143, 248, 152)
        painter.drawLine(256, 152, 290, 152)
        painter.drawLine(290, 152, 302, 144) 
        painter.drawText(290, 135, "SA2")
        painter.drawLine(305, 152, 335, 152)
        
        
        painter.drawRect(335, 145, 35, 14)
        painter.drawText(347, 140, "R2")
        painter.drawLine(352, 145, 352, 130) 
        painter.drawLine(352, 130, 385, 130)
        painter.drawLine(385, 130, 385, 115) 
        painter.drawLine(370, 152, 420, 152) 
        
        
        painter.drawText(230, 185, "~ 220 B")
        painter.drawEllipse(232, 190, 6, 6)
        painter.drawEllipse(258, 190, 6, 6)
        painter.drawLine(235, 190, 235, 162)
        painter.drawLine(261, 190, 261, 162)

       
        painter.drawLine(252, 78, 320, 78)
        
        
        painter.drawEllipse(320, 68, 20, 20)
        painter.drawText(324, 81, "µA")
        painter.drawLine(340, 78, 410, 78) 
        
        
        painter.drawLine(375, 78, 375, 95)
        painter.drawEllipse(365, 95, 20, 20)
        painter.drawText(372, 108, "V")
        painter.drawLine(375, 115, 375, 152) 
        
        
        painter.drawLine(410, 78, 435, 78)
        painter.drawLine(435, 78, 447, 70) 
        painter.drawText(435, 63, "SA3")
        painter.drawLine(450, 78, 510, 78) 
        
       
        painter.drawRect(510, 50, 14, 70)
        painter.drawText(512, 44, "R3")
        
        
        painter.drawLine(495, 85, 510, 85)
        painter.drawLine(495, 85, 495, 78)
        
        
        painter.drawText(570, 45, "к выпрямителю")
        painter.drawEllipse(600, 60, 6, 6)
        painter.drawEllipse(600, 120, 6, 6)
        
        painter.drawLine(517, 63, 600, 63) 
        painter.drawLine(517, 120, 600, 120) 
        painter.drawLine(517, 120, 517, 152)  
        painter.drawLine(420, 152, 517, 152) 
