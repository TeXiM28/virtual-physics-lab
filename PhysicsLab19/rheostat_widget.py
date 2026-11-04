import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush,QFont

class VirtualRheostat(QWidget):
    # Сигнал, который будет срабатывать при движении ползунка
    valueChanged = pyqtSignal(int)

    def __init__(self, name="Реостат", min_val=0, max_val=100, start_val=0):
        super().__init__()
        self.name = name
        self.min_val = min_val
        self.max_val = max_val
        self.value = start_val
        self.setMinimumSize(120, 260)
        self.is_dragging = False

    def setValue(self, val):
        self.value = max(self.min_val, min(val, self.max_val))
        self.update()
        self.valueChanged.emit(self.value)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Рисуем керамическое основание (трубу реостата)
        painter.setBrush(QBrush(QColor("#D7CCC8")))
        painter.setPen(QPen(QColor("#5D4037"), 2))
        rect_x = self.width() // 2 - 25
        rect_y = 40
        rect_w = 50
        rect_h = self.height() - 80
        painter.drawRect(rect_x, rect_y, rect_w, rect_h)

        # Имитация витков обмотки (горизонтальные линии)
        painter.setPen(QPen(QColor("#795548"), 1))
        for y in range(rect_y + 4, rect_y + rect_h - 4, 4):
            painter.drawLine(rect_x + 2, y, rect_x + rect_w - 2, y)

        # Верхняя металлическая направляющая шина
        painter.setBrush(QBrush(QColor("#B0BEC5")))
        painter.setPen(QPen(QColor("#37474F"), 2))
        painter.drawRect(self.width() // 2 - 6, rect_y - 10, 12, rect_h + 20)

        # Вычисление позиции ползунка на основе текущего значения
        norm_val = (self.value - self.min_val) / (self.max_val - self.min_val)
        # Инвертируем, чтобы максимум был вверху, как на реальном РСП
        slider_y = int(rect_y + rect_h - (norm_val * rect_h))

        # Рисуем ползунок (бегунок реостата)
        painter.setBrush(QBrush(QColor("#CFD8DC")))
        painter.setPen(QPen(QColor("#263238"), 2))
        painter.drawRect(self.width() // 2 - 30, slider_y - 12, 60, 24)
        
        # Красный контактный маркер на ползунке
        painter.setBrush(QBrush(QColor("#D32F2F")))
        painter.drawEllipse(self.width() // 2 - 6, slider_y - 6, 12, 12)

        # Подписи
        painter.setPen(QPen(QColor("#FFFFFF")))
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        painter.drawText(10, 20, self.name)
        
        # Текущее значение маленьким шрифтом внизу
        painter.setFont(QFont("Arial", 8))
        painter.drawText(10, self.height() - 15, f"Знач: {self.value}")

    # Логика управления мышкой (Drag-and-Drop ползунка)
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.update_value_from_mouse(event.position().y())

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.update_value_from_mouse(event.position().y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False

    def update_value_from_mouse(self, mouse_y):
        rect_y = 40
        rect_h = self.height() - 80
        # Ограничиваем координаты
        y = max(rect_y, min(mouse_y, rect_y + rect_h))
        # Считаем относительное положение
        norm = (rect_y + rect_h - y) / rect_h
        val = int(self.min_val + norm * (self.max_val - self.min_val))
        self.setValue(val)
