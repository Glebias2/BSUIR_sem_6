"""
Точка входа — запуск графического редактора.
Лабораторная работа №1: Алгоритмы построения отрезков.
"""

import sys
import os

# Исправление ошибки "no Qt platform plugin could be initialized" на Windows
import PyQt5
qt_plugins = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
if os.path.isdir(qt_plugins):
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = qt_plugins

from PyQt5.QtWidgets import QApplication
from editor import EditorWindow


def main():
    app = QApplication(sys.argv)
    window = EditorWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
