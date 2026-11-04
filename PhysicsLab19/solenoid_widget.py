from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt6.QtCore import QPointF

class VirtualSolenoid(QWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(180, 260)
        self.is_active = False

    def setActive(self, state):
        self.is_active = state
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.width() // 2
        cy = self.height() // 2

        # 1. Рисуем каркас катушки соленоида (Цилиндр медного цвета)
        gradient = QLinearGradient(QPointF(cx - 60, cy), QPointF(cx + 60, cy))
        gradient.setColorAt(0.0, QColor("#5D4037"))
        gradient.setColorAt(0.3, QColor("#D84315"))
        gradient.setColorAt(0.7, QColor("#FF8A65"))
        gradient.setColorAt(1.0, QColor("#4E342E"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(QColor("#2E1C0C"), 2))
        painter.drawRect(cx - 60, cy - 90, 120, 180)

        # Витки толстого провода на катушке
        painter.setPen(QPen(QColor("#FF7043"), 2))
        for y in range(cy - 80, cy + 90, 12):
            painter.drawArc(cx - 60, y - 6, 120, 12, 0, 180 * 16)

        # 2. Смотровое окно по центру соленоида (прорезь)
        painter.setBrush(QBrush(QColor("#212121")))
        painter.setPen(QPen(QColor("#000000"), 1))
        painter.drawRect(cx - 20, cy - 50, 40, 100)

        # 3. Электронная вакуумная лампа внутри окна
        if self.is_active:
            # Эффект свечения накала (яркий оранжевый градиент)
            lamp_grad = QLinearGradient(QPointF(cx, cy - 40), QPointF(cx, cy + 40))
            lamp_grad.setColorAt(0.0, QColor("#FF3D00"))
            lamp_grad.setColorAt(0.5, QColor("#FFB300"))
            lamp_grad.setColorAt(1.0, QColor("#FF3D00"))
            painter.setBrush(QBrush(lamp_grad))
        else:
            # Лампа выключена (темное стекло)
            painter.setBrush(QBrush(QColor("#37474F")))

        painter.drawRect(cx - 12, cy - 40, 24, 80)
