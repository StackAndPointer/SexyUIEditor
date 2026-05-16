# -*- coding: utf-8 -*-
"""
Custom Component Dialog
Dialog for creating and editing custom extension components.
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QPushButton, QCheckBox,
    QFileDialog, QMessageBox, QListWidget, QListWidgetItem,
    QComboBox, QGroupBox, QLabel, QWidget, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from core.i18n import tr
from core.extension_manager import ExtensionManager, ExtensionComponentDef, create_default_properties


class PropertyItemWidget(QWidget):
    def __init__(self, prop_data: dict, parent=None):
        super().__init__(parent)
        self._prop_data = prop_data.copy()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self._name_edit = QLineEdit(self._prop_data.get("name", ""))
        self._name_edit.setPlaceholderText(tr("ext.prop_name", "Property name"))
        self._name_edit.setMaximumWidth(120)
        
        self._type_combo = QComboBox()
        self._type_combo.addItems(["int", "float", "string", "bool", "color", "image", "font", "rect", "enum"])
        self._type_combo.setCurrentText(self._prop_data.get("prop_type", "string"))
        self._type_combo.setMaximumWidth(80)
        
        self._display_edit = QLineEdit(self._prop_data.get("display_name", ""))
        self._display_edit.setPlaceholderText(tr("ext.display_name", "Display name"))
        
        self._default_edit = QLineEdit(str(self._prop_data.get("default", "")))
        self._default_edit.setPlaceholderText(tr("ext.default_value", "Default"))
        self._default_edit.setMaximumWidth(80)
        
        self._category_edit = QLineEdit(self._prop_data.get("category", "common"))
        self._category_edit.setPlaceholderText(tr("ext.category", "Category"))
        self._category_edit.setMaximumWidth(80)
        
        self._delete_btn = QPushButton("×")
        self._delete_btn.setMaximumWidth(30)
        self._delete_btn.clicked.connect(self._on_delete)
        
        layout.addWidget(self._name_edit)
        layout.addWidget(self._type_combo)
        layout.addWidget(self._display_edit)
        layout.addWidget(self._default_edit)
        layout.addWidget(self._category_edit)
        layout.addWidget(self._delete_btn)
    
    def _on_delete(self):
        parent = self.parentWidget()
        if parent and isinstance(parent, QListWidget):
            row = parent.row(parent.itemWidget(self))
            if row >= 0:
                parent.takeItem(row)
    
    def get_property_data(self) -> dict:
        return {
            "name": self._name_edit.text(),
            "prop_type": self._type_combo.currentText(),
            "display_name": self._display_edit.text(),
            "default": self._default_edit.text(),
            "category": self._category_edit.text(),
            "enum_values": [],
            "tooltip": "",
        }


class CustomComponentDialog(QDialog):
    def __init__(self, existing_class_name: str = None, platform: str = None, parent=None):
        super().__init__(parent)
        self._existing_class_name = existing_class_name
        self._ext_manager = ExtensionManager.instance()
        self._result_def = None
        self._platform = platform or self._ext_manager._current_platform
        
        self.setWindowTitle(tr("ext.dialog_title", "Custom Component"))
        self.setMinimumSize(800, 600)
        self._setup_ui()
        
        if existing_class_name:
            self._load_existing(existing_class_name)
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        form_group = QGroupBox(tr("ext.basic_info", "Basic Information"))
        form_layout = QFormLayout(form_group)
        
        self._class_name_edit = QLineEdit()
        self._class_name_edit.setPlaceholderText(tr("ext.class_name_hint", "e.g., MyCustomWidget"))
        form_layout.addRow(tr("ext.class_name", "Class Name:"), self._class_name_edit)
        
        self._display_name_edit = QLineEdit()
        self._display_name_edit.setPlaceholderText(tr("ext.display_name_hint", "e.g., My Custom Widget"))
        form_layout.addRow(tr("ext.display_name", "Display Name:"), self._display_name_edit)
        
        self._description_edit = QLineEdit()
        form_layout.addRow(tr("ext.description", "Description:"), self._description_edit)
        
        self._parent_class_edit = QLineEdit()
        self._parent_class_edit.setPlaceholderText("Widget")
        form_layout.addRow(tr("ext.parent_class", "Parent Class:"), self._parent_class_edit)
        
        self._is_container_check = QCheckBox()
        form_layout.addRow(tr("ext.is_container", "Is Container:"), self._is_container_check)
        
        left_layout.addWidget(form_group)
        
        props_group = QGroupBox(tr("ext.properties", "Properties"))
        props_layout = QVBoxLayout(props_group)
        
        props_header = QHBoxLayout()
        add_prop_btn = QPushButton(tr("ext.add_property", "Add Property"))
        add_prop_btn.clicked.connect(self._add_default_property)
        add_default_btn = QPushButton(tr("ext.add_base_props", "Add Base Props"))
        add_default_btn.clicked.connect(self._add_base_properties)
        props_header.addWidget(add_prop_btn)
        props_header.addWidget(add_default_btn)
        props_header.addStretch()
        props_layout.addLayout(props_header)
        
        self._props_list = QListWidget()
        props_layout.addWidget(self._props_list)
        
        left_layout.addWidget(props_group)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        cpp_group = QGroupBox(tr("ext.cpp_code", "C++ Code"))
        cpp_layout = QVBoxLayout(cpp_group)
        
        cpp_btn_layout = QHBoxLayout()
        import_header_btn = QPushButton(tr("ext.import_header", "Import .h"))
        import_header_btn.clicked.connect(self._import_cpp_header)
        import_source_btn = QPushButton(tr("ext.import_source", "Import .cpp"))
        import_source_btn.clicked.connect(self._import_cpp_source)
        cpp_btn_layout.addWidget(import_header_btn)
        cpp_btn_layout.addWidget(import_source_btn)
        cpp_btn_layout.addStretch()
        cpp_layout.addLayout(cpp_btn_layout)
        
        self._cpp_header_edit = QTextEdit()
        self._cpp_header_edit.setPlaceholderText(tr("ext.header_hint", "C++ header file content..."))
        self._cpp_header_edit.setFontFamily("Consolas")
        cpp_layout.addWidget(QLabel(tr("ext.header", "Header (.h):")))
        cpp_layout.addWidget(self._cpp_header_edit)
        
        self._cpp_source_edit = QTextEdit()
        self._cpp_source_edit.setPlaceholderText(tr("ext.source_hint", "C++ source file content..."))
        self._cpp_source_edit.setFontFamily("Consolas")
        cpp_layout.addWidget(QLabel(tr("ext.source", "Source (.cpp):")))
        cpp_layout.addWidget(self._cpp_source_edit)
        
        right_layout.addWidget(cpp_group)
        
        csharp_group = QGroupBox(tr("ext.csharp_code", "C# Code"))
        csharp_layout = QVBoxLayout(csharp_group)
        
        cs_btn_layout = QHBoxLayout()
        import_cs_btn = QPushButton(tr("ext.import_cs", "Import .cs"))
        import_cs_btn.clicked.connect(self._import_csharp)
        cs_btn_layout.addWidget(import_cs_btn)
        cs_btn_layout.addStretch()
        csharp_layout.addLayout(cs_btn_layout)
        
        self._csharp_edit = QTextEdit()
        self._csharp_edit.setPlaceholderText(tr("ext.csharp_hint", "C# source file content..."))
        self._csharp_edit.setFontFamily("Consolas")
        csharp_layout.addWidget(self._csharp_edit)
        
        right_layout.addWidget(csharp_group)
        
        if self._platform == "cpp":
            csharp_group.hide()
        else:
            cpp_group.hide()
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])
        
        layout.addWidget(splitter)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton(tr("btn.ok", "OK"))
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton(tr("btn.cancel", "Cancel"))
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
    
    def _add_default_property(self):
        prop_data = {"name": "", "prop_type": "string", "display_name": "", "default": "", "category": "common"}
        self._add_property_widget(prop_data)
    
    def _add_base_properties(self):
        for prop_data in create_default_properties():
            self._add_property_widget(prop_data)
    
    def _add_property_widget(self, prop_data: dict):
        item = QListWidgetItem(self._props_list)
        widget = PropertyItemWidget(prop_data, self._props_list)
        item.setSizeHint(widget.sizeHint())
        self._props_list.setItemWidget(item, widget)
    
    def _import_cpp_header(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("ext.select_header", "Select Header File"), "",
            "C++ Header (*.h);;All Files (*)"
        )
        if filepath:
            content = self._ext_manager.import_cpp_files(filepath.split('/')[-1].split('\\')[-1].replace('.h', ''), header_path=filepath)[0]
            self._cpp_header_edit.setPlainText(content)
    
    def _import_cpp_source(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("ext.select_source", "Select Source File"), "",
            "C++ Source (*.cpp);;All Files (*)"
        )
        if filepath:
            content = self._ext_manager.import_cpp_files(None, source_path=filepath)[1]
            self._cpp_source_edit.setPlainText(content)
    
    def _import_csharp(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("ext.select_cs", "Select C# File"), "",
            "C# Source (*.cs);;All Files (*)"
        )
        if filepath:
            content = self._ext_manager.import_csharp_file(filepath)
            self._csharp_edit.setPlainText(content)
    
    def _load_existing(self, class_name: str):
        ext_def = self._ext_manager.get_extension(class_name)
        if ext_def:
            self._class_name_edit.setText(ext_def.class_name)
            self._class_name_edit.setReadOnly(True)
            self._display_name_edit.setText(ext_def.display_name)
            self._description_edit.setText(ext_def.description)
            self._parent_class_edit.setText(ext_def.parent_class)
            self._is_container_check.setChecked(ext_def.is_container)
            
            for prop in ext_def.properties:
                self._add_property_widget(prop)
            
            if self._platform == "cpp":
                self._cpp_header_edit.setPlainText(ext_def.header_code)
                self._cpp_source_edit.setPlainText(ext_def.source_code)
            else:
                self._csharp_edit.setPlainText(ext_def.source_code)
    
    def _on_save(self):
        class_name = self._class_name_edit.text().strip()
        if not class_name:
            QMessageBox.warning(self, tr("error.title", "Error"), tr("ext.class_name_required", "Class name is required"))
            return
        
        if not class_name[0].isalpha() and class_name[0] != '_':
            QMessageBox.warning(self, tr("error.title", "Error"), tr("ext.invalid_class_name", "Class name must start with a letter or underscore"))
            return
        
        properties = []
        for i in range(self._props_list.count()):
            item = self._props_list.item(i)
            widget = self._props_list.itemWidget(item)
            if widget:
                prop_data = widget.get_property_data()
                if prop_data.get("name"):
                    properties.append(prop_data)
        
        ext_def = ExtensionComponentDef(
            class_name=class_name,
            display_name=self._display_name_edit.text().strip() or class_name,
            description=self._description_edit.text().strip(),
            parent_class=self._parent_class_edit.text().strip() or "Widget",
            is_container=self._is_container_check.isChecked(),
            properties=properties,
            source_code=self._cpp_source_edit.toPlainText() if self._platform == "cpp" else self._csharp_edit.toPlainText(),
            header_code=self._cpp_header_edit.toPlainText() if self._platform == "cpp" else "",
            platform=self._platform,
        )
        
        if self._ext_manager.save_extension(ext_def):
            self._result_def = ext_def
            self.accept()
        else:
            QMessageBox.warning(self, tr("error.title", "Error"), tr("ext.save_failed", "Failed to save extension"))
    
    def get_result(self) -> ExtensionComponentDef:
        return self._result_def
