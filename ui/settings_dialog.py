# -*- coding: utf-8 -*-
from core.qt_compat import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QSpinBox, QCheckBox, QPushButton, QHBoxLayout,
    QListWidget, QGroupBox, QComboBox, QLabel, Qt
)
from core.project import Project, ProjectSettings
from core.resource_manager import ResourceManager
from core.code_generator import CodeGenerator
from core.i18n import tr
from ui.dark_titlebar import set_transparent_titlebar
from ui.image_picker import ImagePickerDialog

_LISTENERS = [
    "ButtonListener", "DialogListener", "EditListener",
    "ListListener", "CheckboxListener", "SliderListener", "ScrollListener"
]


class SettingsDialog(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        set_transparent_titlebar(self)
        self._project = project
        self._settings = project.current_interface.settings if project.current_interface else ProjectSettings()
        self._res_mgr = ResourceManager.instance()
        self._code_gen = CodeGenerator.instance()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(tr("settings.title", "Project Settings"))
        self.resize(450, 600)

        layout = QVBoxLayout(self)

        basic_group = QGroupBox(tr("settings.basic", "Basic"))
        basic_form = QFormLayout()

        self._class_name = QLineEdit(self._settings.class_name)
        basic_form.addRow(tr("settings.class_name", "Class Name:"), self._class_name)

        self._namespace = QLineEdit(self._project.settings.namespace)
        basic_form.addRow(tr("settings.namespace", "Namespace:"), self._namespace)

        self._parent_class = QLineEdit(self._settings.parent_class)
        basic_form.addRow(tr("settings.parent_class", "Parent Class:"), self._parent_class)

        self._header_include = QLineEdit(self._project.settings.header_include)
        basic_form.addRow(tr("settings.header_include", "Header Include:"), self._header_include)

        self._width = QSpinBox()
        self._width.setRange(100, 4096)
        self._width.setValue(self._settings.width)
        basic_form.addRow(tr("settings.width", "Width:"), self._width)

        self._height = QSpinBox()
        self._height.setRange(100, 4096)
        self._height.setValue(self._settings.height)
        basic_form.addRow(tr("settings.height", "Height:"), self._height)

        basic_group.setLayout(basic_form)
        layout.addWidget(basic_group)

        bg_group = QGroupBox(tr("settings.background", "Background"))
        bg_form = QFormLayout()

        current_bg = self._settings.background_image
        self._bg_image_btn = QPushButton(current_bg or tr("settings.select_image", "Select Image..."))
        self._bg_image_btn.clicked.connect(self._pick_bg_image)
        bg_form.addRow(tr("settings.bg_image", "Background Image:"), self._bg_image_btn)

        self._bg_stretch = QCheckBox(tr("settings.bg_stretch", "Stretch to canvas"))
        self._bg_stretch.setChecked(self._settings.background_stretch)
        bg_form.addRow("", self._bg_stretch)

        self._bg_color = QLineEdit(self._settings.background_color)
        self._bg_color.setPlaceholderText("R,G,B (e.g. 0,0,0)")
        bg_form.addRow(tr("settings.bg_color", "Background Color:"), self._bg_color)

        bg_group.setLayout(bg_form)
        layout.addWidget(bg_group)

        listener_group = QGroupBox(tr("settings.listeners", "Listeners"))
        listener_layout = QVBoxLayout()
        
        auto_label = QLabel(tr("settings.auto_detected", "(Auto-detected listeners are checked)"))
        auto_label.setStyleSheet("color: #888; font-style: italic;")
        listener_layout.addWidget(auto_label)
        
        self._listener_checks = {}
        iface = self._project.current_interface
        required = self._code_gen._get_required_listeners_for_interface(iface) if iface else set()
        for l in _LISTENERS:
            cb = QCheckBox(l)
            is_required = l in required
            cb.setChecked(is_required or l in self._settings.listeners)
            if is_required:
                cb.setStyleSheet("color: #4a9eff;")
            self._listener_checks[l] = cb
            listener_layout.addWidget(cb)
        listener_group.setLayout(listener_layout)
        layout.addWidget(listener_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._ok_btn = QPushButton(tr("btn.ok", "OK"))
        self._cancel_btn = QPushButton(tr("btn.cancel", "Cancel"))
        btn_layout.addWidget(self._ok_btn)
        btn_layout.addWidget(self._cancel_btn)
        layout.addLayout(btn_layout)

        self._ok_btn.clicked.connect(self._on_ok)
        self._cancel_btn.clicked.connect(self.reject)

    def _pick_bg_image(self):
        current = self._bg_image_btn.text()
        if current == tr("settings.select_image", "Select Image..."):
            current = ""
        platform = self._project.settings.target_platform
        dialog = ImagePickerDialog(current, "image", self, platform=platform)
        if dialog.exec():
            selected = dialog.get_selected_value()
            self._bg_image_btn.setText(selected or tr("settings.select_image", "Select Image..."))

    def _on_ok(self):
        self._settings.class_name = self._class_name.text()
        self._project.settings.namespace = self._namespace.text()
        self._settings.parent_class = self._parent_class.text()
        self._project.settings.header_include = self._header_include.text()
        self._settings.width = self._width.value()
        self._settings.height = self._height.value()
        bg_text = self._bg_image_btn.text()
        if bg_text == tr("settings.select_image", "Select Image..."):
            self._settings.background_image = ""
        else:
            self._settings.background_image = bg_text
        self._settings.background_stretch = self._bg_stretch.isChecked()
        self._settings.background_color = self._bg_color.text()
        self._settings.listeners = [
            l for l, cb in self._listener_checks.items() if cb.isChecked()
        ]
        self.accept()
