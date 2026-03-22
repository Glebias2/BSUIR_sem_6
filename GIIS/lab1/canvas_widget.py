"""
Виджет пользовательского режима — холст для рисования отрезков.
Поддерживает ввод мышью (два клика) и отрисовку результатов алгоритмов.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QMouseEvent, QPen
from PyQt5.QtCore import Qt, pyqtSignal


class CanvasWidget(QWidget):
    """Холст для рисования отрезков в пользовательском режиме."""

    # Сигнал: пользователь задал отрезок мышью (x1, y1, x2, y2)
    line_drawn = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("background-color: white;")

        self._points = []          # список (x, y, intensity) для отрисовки
        self._click_start = None   # первый клик мышью
        self._preview_end = None   # текущая позиция мыши (для предпросмотра)
        self.setMouseTracking(True)

    def set_points(self, points):
        """Установить точки для отрисовки."""
        self._points = points
        self.update()

    def clear(self):
        """Очистить холст."""
        self._points = []
        self._click_start = None
        self._preview_end = None
        self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            x, y = event.x(), event.y()
            if self._click_start is None:
                self._click_start = (x, y)
            else:
                x1, y1 = self._click_start
                self._click_start = None
                self._preview_end = None
                self.line_drawn.emit(x1, y1, x, y)

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._click_start is not None:
            self._preview_end = (event.x(), event.y())
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        # Рисуем отрезки — каждый пиксель как квадрат 1x1
        for (px, py, intensity) in self._points:
            alpha = max(0, min(255, int(intensity * 255)))
            color = QColor(0, 0, 0, alpha)
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(px, py, 1, 1)

        # Предпросмотр: тонкая линия от первого клика к курсору
        if self._click_start and self._preview_end:
            pen = QPen(QColor(100, 100, 255, 150), 1, Qt.DashLine)
            painter.setPen(pen)
            painter.drawLine(self._click_start[0], self._click_start[1],
                             self._preview_end[0], self._preview_end[1])
            # Точка начала
            painter.setBrush(QColor(255, 0, 0))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(self._click_start[0] - 3, self._click_start[1] - 3, 6, 6)

        painter.end()
