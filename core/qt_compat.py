# -*- coding: utf-8 -*-
"""
Qt Compatibility Layer

This module provides a unified interface for PyQt6 and PySide6,
allowing the application to work on macOS where Nuitka only supports PySide6.

Usage:
    from core.qt_compat import QtWidgets, QtCore, QtGui, Signal

On Windows/Linux: Uses PyQt6
On macOS: Uses PySide6 (for Nuitka compatibility)
"""

import sys
import os

# Force PySide6 on macOS for Nuitka compatibility
# Can be overridden with environment variable QT_BINDING
FORCE_PYSIDE6 = sys.platform == "darwin"
QT_BINDING = os.environ.get("QT_BINDING", "auto")

if QT_BINDING == "pyside6" or (QT_BINDING == "auto" and FORCE_PYSIDE6):
    # Use PySide6
    from PySide6.QtWidgets import *
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    
    # PySide6 uses Signal instead of pyqtSignal
    Signal = Signal
    Slot = Slot
    Property = Property
    
    QT_BINDING_NAME = "PySide6"
else:
    # Use PyQt6 (default for Windows/Linux)
    from PyQt6.QtWidgets import *
    from PyQt6.QtCore import *
    from PyQt6.QtGui import *
    
    # PyQt6 uses pyqtSignal, map to Signal for compatibility
    Signal = pyqtSignal
    Slot = pyqtSlot
    Property = pyqtProperty
    
    QT_BINDING_NAME = "PyQt6"

# Export common classes that might be imported directly
__all__ = [
    # QtWidgets
    "QApplication", "QWidget", "QMainWindow", "QDialog", "QMessageBox",
    "QVBoxLayout", "QHBoxLayout", "QGridLayout", "QScrollArea",
    "QPushButton", "QLabel", "QLineEdit", "QTextEdit", "QComboBox",
    "QCheckBox", "QTreeWidget", "QTreeWidgetItem", "QTabWidget",
    "QFileDialog", "QMenu", "QMenuBar", "QToolBar", "QStatusBar",
    "QSplitter", "QGroupBox", "QSpinBox", "QDoubleSpinBox",
    "QSlider", "QProgressBar", "QListWidget", "QTableWidget",
    "QAction", "QActionGroup", "QSizePolicy",
    
    # QtCore
    "Qt", "QObject", "QSize", "QPoint", "QRect", "QSettings",
    "QTimer", "QEvent", "QMimeData", "QRegularExpression",
    "Signal", "Slot", "Property",
    
    # QtGui
    "QPainter", "QPen", "QBrush", "QColor", "QFont", "QPixmap",
    "QIcon", "QImage", "QDrag", "QCursor", "QKeySequence",
    "QSyntaxHighlighter", "QTextCharFormat",
    "QMouseEvent", "QWheelEvent", "QDragEnterEvent", "QDropEvent",
    
    # Module info
    "QT_BINDING_NAME",
]