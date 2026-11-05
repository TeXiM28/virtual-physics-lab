import math
import random
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QBrush

class ArrowInstrument(QWidget):
    def __init__(self, name="Микроамперметр", unit="мкА", max_val=1000.0, accuracy_class=1.5):
        super().__init__()
        self.name = name
        self.unit = unit
        self.max_val = max_val
        self.accuracy_class = accuracy_class
        self.real_value = 0.0          
        self.displayed_value = 0.0     
        self.setMinimumSize(180, 180)
        
    def set_value(self, val):
        self.real_value = max(0.0, min(val, self.max_val))
        if self.real_value > 0:
            max_error = (self.accuracy_class / 100.0) * self.max_val
            error = random.uniform(-max_error, max_error)
            self.displayed_value = max(0.0, min(self.real_value + error, self.max_val))
        else:
            self.displayed_value = 0.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Корпус
        painter.setBrush(QColor("#FFFFFF"))
        painter.setPen(QPen(QColor("#2B2B2B"), 2))
        painter.drawRect(5, 5, self.width() - 10, self.height() - 10)
        
        cx = self.width() // 2
        cy = self.height() - 65  
        r = int(min(self.width(), self.height()) * 0.38)
        
        # Дуга шкалы
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.drawArc(cx - r, cy - r, r * 2, r * 2, 0 * 16, 180 * 16)
        
        # Новая цифровая шкала: деления от 0 до 1000 с шагом 20
        painter.setFont(QFont("Arial", 7))
        
        for tick in range (0, 1001, 20):
            tick_angle = 180.0 - (tick / self.max_val) * 180.0
            tick_rad = math.radians(tick_angle)
            
            #Длина засечек
            if tick % 200 == 0:
                tick_len = 12
            elif tick % 100 == 0:
                tick_len = 8
            else: 
                tick_len = 4
            
            # Засечки делений
            x_start = cx + r * math.cos(tick_rad)
            y_start = cy - r * math.sin(tick_rad)
            x_end = cx + (r - tick_len) * math.cos(tick_rad)
            y_end = cy - (r - tick_len) * math.sin(tick_rad)
            
            painter.setPen(QPen(QColor("#000000"), 1.5 if tick % 100 == 0 else 1.0))
            painter.drawLine(int(x_start), int(y_start), int(x_end), int(y_end))
            
            # Цифровые подписи
            if tick % 200 == 0:
                x_text = cx + (r - 25) * math.cos(tick_rad) - 10
                y_text = cy - (r - 25) * math.sin(tick_rad) + 4
                painter.drawText(int(x_text), int(y_text), str(tick))
            
        # Стрелка
        angle_deg = 180.0 - (self.displayed_value / self.max_val) * 180.0
        angle_rad = math.radians(angle_deg)
        ax = cx + (r - 5) * math.cos(angle_rad)
        ay = cy - (r - 5) * math.sin(angle_rad)
        
        painter.setPen(QPen(QColor("#E74C3C"), 2)) 
        painter.drawLine(cx, cy, int(ax), int(ay))
        
        painter.setBrush(QColor("#000000"))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawEllipse(cx - 4, cy - 4, 8, 8)
        
        # Дисплей (ЖК)
        painter.setBrush(QColor("#2C3E50"))
        painter.drawRect(cx - 45, cy + 15, 90, 25)
        painter.setBrush(QColor("#A9DFBF"))
        painter.drawRect(cx - 41, cy + 18, 82, 19)
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        
        # Вывод формата с поддержкой значений до 1000
        painter.drawText(cx - 36, cy + 32, f"{self.displayed_value:0.1f}")
        
        # Метки прибора
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.drawText(cx - 55, cy + 55, f"{self.name} ({self.unit})")
        
        painter.setFont(QFont("Arial", 7))
        painter.drawText(12, 20, f"Кл. точн. {self.accuracy_class}")