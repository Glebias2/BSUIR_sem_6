"""
Виджет отладочного режима — дискретная сетка с пошаговой визуализацией
работы алгоритмов построения отрезков.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QSplitter,
                             QHeaderView, QLabel, QSlider)
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, pyqtSignal


class GridWidget(QWidget):
    """Виджет дискретной сетки для отладочного отображения."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 400)

        self._cell_size = 30
        self._points = []          # все точки (x, y, intensity)
        self._visible_count = 0    # сколько точек показывать (для пошагового режима)
        self._offset_x = 20        # отступ для подписей осей
        self._offset_y = 20

        # Границы отображаемой области
        self._min_x = 0
        self._min_y = 0
        self._max_x = 10
        self._max_y = 10

    def set_data(self, points, show_all=True):
        """Установить точки и пересчитать границы сетки."""
        self._points = points
        if points:
            xs = [p[0] for p in points]
            ys = [p[1] for p in points]
            self._min_x = min(xs) - 1
            self._min_y = min(ys) - 1
            self._max_x = max(xs) + 2
            self._max_y = max(ys) + 2
        else:
            self._min_x, self._min_y = 0, 0
            self._max_x, self._max_y = 10, 10

        self._visible_count = len(points) if show_all else 0
        self.update()

    def set_visible_count(self, count):
        """Показать первые count точек (пошаговый режим)."""
        self._visible_count = min(count, len(self._points))
        self.update()

    def set_cell_size(self, size):
        self._cell_size = max(10, min(80, size))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, False)

        cs = self._cell_size
        cols = self._max_x - self._min_x
        rows = self._max_y - self._min_y
        ox = self._offset_x
        oy = self._offset_y

        # Фон
        painter.fillRect(self.rect(), QColor(255, 255, 255))

        # Рисуем сетку
        pen_grid = QPen(QColor(220, 220, 220), 1)
        painter.setPen(pen_grid)
        for col in range(cols + 1):
            x = ox + col * cs
            painter.drawLine(x, oy, x, oy + rows * cs)
        for row in range(rows + 1):
            y = oy + row * cs
            painter.drawLine(ox, y, ox + cols * cs, y)

        # Подписи осей
        painter.setPen(QColor(80, 80, 80))
        font = QFont("Arial", max(7, cs // 4))
        painter.setFont(font)
        for col in range(cols):
            val = self._min_x + col
            x = ox + col * cs + cs // 2
            painter.drawText(x - 8, oy - 4, str(val))
        for row in range(rows):
            val = self._min_y + row
            y = oy + row * cs + cs // 2 + 4
            painter.drawText(2, y, str(val))

        # Рисуем идеальную линию (если есть хотя бы 2 точки)
        if len(self._points) >= 2:
            first = self._points[0]
            last = self._points[-1]
            pen_line = QPen(QColor(200, 200, 255), 1, Qt.DashLine)
            painter.setPen(pen_line)
            fx = ox + (first[0] - self._min_x) * cs + cs // 2
            fy = oy + (first[1] - self._min_y) * cs + cs // 2
            lx = ox + (last[0] - self._min_x) * cs + cs // 2
            ly = oy + (last[1] - self._min_y) * cs + cs // 2
            painter.drawLine(fx, fy, lx, ly)

        # Закрашиваем пиксели
        for idx, (px, py, intensity) in enumerate(self._points):
            if idx >= self._visible_count:
                break
            alpha = max(0, min(255, int(intensity * 255)))
            color = QColor(50, 120, 200, alpha)
            col = px - self._min_x
            row = py - self._min_y
            x = ox + col * cs + 1
            y = oy + row * cs + 1
            painter.setPen(Qt.NoPen)
            painter.setBrush(color)
            painter.drawRect(x, y, cs - 2, cs - 2)

            # Номер шага внутри ячейки
            if cs >= 25:
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(x + 2, y + cs - 6, str(idx))

        painter.end()


class DebugWidget(QWidget):
    """Полный виджет отладочного режима: сетка + таблица + кнопки."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._steps = []
        self._points = []
        self._current_step = 0
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        # Панель управления
        control_layout = QHBoxLayout()

        self.btn_reset = QPushButton("Сброс")
        self.btn_step = QPushButton("Следующий шаг")
        self.btn_all = QPushButton("Все шаги")

        self.btn_reset.clicked.connect(self._on_reset)
        self.btn_step.clicked.connect(self._on_next_step)
        self.btn_all.clicked.connect(self._on_show_all)

        control_layout.addWidget(self.btn_reset)
        control_layout.addWidget(self.btn_step)
        control_layout.addWidget(self.btn_all)

        # Слайдер масштаба сетки
        control_layout.addWidget(QLabel("Масштаб:"))
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setRange(10, 80)
        self.zoom_slider.setValue(30)
        self.zoom_slider.valueChanged.connect(self._on_zoom)
        control_layout.addWidget(self.zoom_slider)

        layout.addLayout(control_layout)

        # Сплиттер: сетка слева, таблица справа
        splitter = QSplitter(Qt.Horizontal)

        self.grid_widget = GridWidget()
        splitter.addWidget(self.grid_widget)

        self.table = QTableWidget()
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.currentCellChanged.connect(self._on_table_row_changed)
        splitter.addWidget(self.table)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        layout.addWidget(splitter)

    def set_data(self, result, algorithm_name=""):
        """Установить результат работы алгоритма."""
        self._points = result.get("points", [])
        self._steps = result.get("steps", [])
        self._current_step = 0

        self.grid_widget.set_data(self._points, show_all=False)
        self.grid_widget.set_visible_count(0)

        self._fill_table(algorithm_name)

    def _fill_table(self, algorithm_name):
        """Заполнить таблицу данными шагов."""
        if not self._steps:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return

        columns = list(self._steps[0].keys())
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(len(self._steps))

        for row, step in enumerate(self._steps):
            for col, key in enumerate(columns):
                val = step.get(key, "")
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _on_reset(self):
        self._current_step = 0
        self.grid_widget.set_visible_count(0)
        self.table.clearSelection()

    def _on_next_step(self):
        if self._current_step < len(self._points):
            self._current_step += 1
            self.grid_widget.set_visible_count(self._current_step)
            # Выделяем строку в таблице
            row = min(self._current_step - 1, self.table.rowCount() - 1)
            if row >= 0:
                self.table.selectRow(row)

    def _on_show_all(self):
        self._current_step = len(self._points)
        self.grid_widget.set_visible_count(self._current_step)

    def _on_zoom(self, value):
        self.grid_widget.set_cell_size(value)

    def _on_table_row_changed(self, current_row, current_col, prev_row, prev_col):
        if current_row >= 0:
            self.grid_widget.set_visible_count(current_row + 1)
            self._current_step = current_row + 1

    def clear(self):
        self._points = []
        self._steps = []
        self._current_step = 0
        self.grid_widget.set_data([], show_all=True)
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
