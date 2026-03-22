"""
Главное окно графического редактора.
Меню, панель инструментов «Отрезки», панель ввода координат,
переключение между пользовательским и отладочным режимами.
"""

from PyQt5.QtWidgets import (QMainWindow, QAction, QActionGroup, QToolBar,
                             QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QSpinBox, QPushButton, QStackedWidget,
                             QStatusBar, QGroupBox, QRadioButton, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

from algorithms import dda, bresenham, wu
from canvas_widget import CanvasWidget
from debug_widget import DebugWidget


ALGORITHMS = {
    "ЦДА": dda,
    "Брезенхем": bresenham,
    "Ву": wu,
}


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Графический редактор — Лаб. 1: Отрезки")
        self.setMinimumSize(900, 650)

        self._current_algorithm = "ЦДА"
        self._init_ui()
        self._update_status()

    # ------------------------------------------------------------------ UI
    def _init_ui(self):
        # ---------- Меню ----------
        menubar = self.menuBar()
        menu_lines = menubar.addMenu("Отрезки")

        self._algo_actions = {}
        algo_group = QActionGroup(self)
        algo_group.setExclusive(True)
        for name in ALGORITHMS:
            action = QAction(name, self, checkable=True)
            action.setData(name)
            action.triggered.connect(self._on_algorithm_selected)
            algo_group.addAction(action)
            menu_lines.addAction(action)
            self._algo_actions[name] = action
        self._algo_actions["ЦДА"].setChecked(True)

        # ---------- Панель инструментов «Отрезки» ----------
        toolbar = QToolBar("Отрезки")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        for name in ALGORITHMS:
            toolbar.addAction(self._algo_actions[name])

        toolbar.addSeparator()

        # Кнопка очистки
        clear_action = QAction("Очистить", self)
        clear_action.triggered.connect(self._on_clear)
        toolbar.addAction(clear_action)

        # ---------- Центральная область ----------
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        # --- Верхняя панель: режим + координаты ---
        top_panel = QHBoxLayout()

        # Переключатель режима
        mode_group = QGroupBox("Режим")
        mode_layout = QHBoxLayout(mode_group)
        self.rb_user = QRadioButton("Пользовательский")
        self.rb_debug = QRadioButton("Отладочный")
        self.rb_user.setChecked(True)
        self.rb_user.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.rb_user)
        mode_layout.addWidget(self.rb_debug)
        top_panel.addWidget(mode_group)

        # Ввод координат
        coord_group = QGroupBox("Координаты")
        coord_layout = QHBoxLayout(coord_group)
        self.spin_x1 = QSpinBox()
        self.spin_y1 = QSpinBox()
        self.spin_x2 = QSpinBox()
        self.spin_y2 = QSpinBox()
        for spin in (self.spin_x1, self.spin_y1, self.spin_x2, self.spin_y2):
            spin.setRange(-1000, 1000)
            spin.setValue(0)

        self.spin_x1.setValue(0)
        self.spin_y1.setValue(0)
        self.spin_x2.setValue(9)
        self.spin_y2.setValue(4)

        coord_layout.addWidget(QLabel("x1:"))
        coord_layout.addWidget(self.spin_x1)
        coord_layout.addWidget(QLabel("y1:"))
        coord_layout.addWidget(self.spin_y1)
        coord_layout.addWidget(QLabel("x2:"))
        coord_layout.addWidget(self.spin_x2)
        coord_layout.addWidget(QLabel("y2:"))
        coord_layout.addWidget(self.spin_y2)

        self.btn_build = QPushButton("Построить")
        self.btn_build.clicked.connect(self._on_build)
        coord_layout.addWidget(self.btn_build)

        top_panel.addWidget(coord_group)
        main_layout.addLayout(top_panel)

        # --- Стек виджетов: пользовательский / отладочный ---
        self.stack = QStackedWidget()
        self.canvas_widget = CanvasWidget()
        self.debug_widget = DebugWidget()

        self.canvas_widget.line_drawn.connect(self._on_line_drawn_mouse)

        self.stack.addWidget(self.canvas_widget)
        self.stack.addWidget(self.debug_widget)
        main_layout.addWidget(self.stack)

        # ---------- Статусбар ----------
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

    # ------------------------------------------------------------------ Обработчики
    def _on_algorithm_selected(self):
        action = self.sender()
        if action:
            self._current_algorithm = action.data()
            self._update_status()

    def _on_mode_changed(self, checked):
        if self.rb_user.isChecked():
            self.stack.setCurrentWidget(self.canvas_widget)
        else:
            self.stack.setCurrentWidget(self.debug_widget)
        self._update_status()

    def _on_build(self):
        x1 = self.spin_x1.value()
        y1 = self.spin_y1.value()
        x2 = self.spin_x2.value()
        y2 = self.spin_y2.value()
        self._run_algorithm(x1, y1, x2, y2)

    def _on_line_drawn_mouse(self, x1, y1, x2, y2):
        """Вызывается при рисовании мышью на canvas."""
        self.spin_x1.setValue(x1)
        self.spin_y1.setValue(y1)
        self.spin_x2.setValue(x2)
        self.spin_y2.setValue(y2)
        self._run_algorithm(x1, y1, x2, y2)

    def _on_clear(self):
        self.canvas_widget.clear()
        self.debug_widget.clear()

    def _run_algorithm(self, x1, y1, x2, y2):
        algo_func = ALGORITHMS[self._current_algorithm]
        result = algo_func(x1, y1, x2, y2)

        # Обновляем оба виджета
        self.canvas_widget.set_points(result["points"])
        self.debug_widget.set_data(result, self._current_algorithm)

        self._update_status(
            f"Отрезок ({x1},{y1})→({x2},{y2}) | "
            f"Пикселей: {len(result['points'])} | Шагов: {len(result['steps'])}"
        )

    def _update_status(self, extra=""):
        mode = "Пользовательский" if self.rb_user.isChecked() else "Отладочный"
        text = f"Алгоритм: {self._current_algorithm} | Режим: {mode}"
        if extra:
            text += f" | {extra}"
        self.status_bar.showMessage(text)
