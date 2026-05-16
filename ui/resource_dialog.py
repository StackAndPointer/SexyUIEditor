# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QPushButton, QFileDialog,
    QInputDialog, QMessageBox, QHeaderView, QSpinBox
)
from PyQt6.QtCore import Qt
from core.resource_manager import ResourceManager
from core.i18n import tr
from ui.dark_titlebar import set_transparent_titlebar


class ResourceDialog(QDialog):
    def __init__(self, res_mgr: ResourceManager, parent=None):
        super().__init__(parent)
        set_transparent_titlebar(self)
        self._res_mgr = res_mgr
        self._setup_ui()
        self._populate()

    def _setup_ui(self):
        self.setWindowTitle(tr("res.title", "Resource Manager"))
        self.resize(600, 450)

        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        self._img_table = QTableWidget(0, 4)
        self._img_table.setHorizontalHeaderLabels([
            tr("res.name", "Name"),
            tr("res.file_path", "File Path"),
            tr("res.rows", "Rows"),
            tr("res.cols", "Cols"),
        ])
        self._img_table.horizontalHeader().setStretchLastSection(True)
        self._img_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        img_widget = QWidget()
        img_layout = QVBoxLayout(img_widget)
        img_layout.addWidget(self._img_table)
        img_btn_layout = QHBoxLayout()
        self._add_img_btn = QPushButton(tr("res.add_image", "Add Image"))
        self._rm_img_btn = QPushButton(tr("res.remove", "Remove"))
        img_btn_layout.addWidget(self._add_img_btn)
        img_btn_layout.addWidget(self._rm_img_btn)
        img_btn_layout.addStretch()
        img_layout.addLayout(img_btn_layout)
        self._tabs.addTab(img_widget, tr("res.images", "Images"))

        self._font_table = QTableWidget(0, 3)
        self._font_table.setHorizontalHeaderLabels([
            tr("res.name", "Name"),
            tr("res.file_path", "File Path"),
            tr("res.point_size", "Point Size"),
        ])
        self._font_table.horizontalHeader().setStretchLastSection(True)
        self._font_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        font_widget = QWidget()
        font_layout = QVBoxLayout(font_widget)
        font_layout.addWidget(self._font_table)
        font_btn_layout = QHBoxLayout()
        self._add_font_btn = QPushButton(tr("res.add_font", "Add Font"))
        self._rm_font_btn = QPushButton(tr("res.remove", "Remove"))
        font_btn_layout.addWidget(self._add_font_btn)
        font_btn_layout.addWidget(self._rm_font_btn)
        font_btn_layout.addStretch()
        font_layout.addLayout(font_btn_layout)
        self._tabs.addTab(font_widget, tr("res.fonts", "Fonts"))

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._ok_btn = QPushButton(tr("btn.ok", "OK"))
        self._cancel_btn = QPushButton(tr("btn.cancel", "Cancel"))
        btn_layout.addWidget(self._ok_btn)
        btn_layout.addWidget(self._cancel_btn)
        layout.addLayout(btn_layout)

        self._add_img_btn.clicked.connect(self._add_image)
        self._rm_img_btn.clicked.connect(self._remove_image)
        self._add_font_btn.clicked.connect(self._add_font)
        self._rm_font_btn.clicked.connect(self._remove_font)
        self._ok_btn.clicked.connect(self.accept)
        self._cancel_btn.clicked.connect(self.reject)

    def _populate(self):
        self._img_table.setRowCount(0)
        for name, img in self._res_mgr.all_images().items():
            row = self._img_table.rowCount()
            self._img_table.insertRow(row)
            self._img_table.setItem(row, 0, QTableWidgetItem(name))
            self._img_table.setItem(row, 1, QTableWidgetItem(img.file_path))
            self._img_table.setItem(row, 2, QTableWidgetItem(str(img.rows)))
            self._img_table.setItem(row, 3, QTableWidgetItem(str(img.cols)))

        self._font_table.setRowCount(0)
        for name, fnt in self._res_mgr.all_fonts().items():
            row = self._font_table.rowCount()
            self._font_table.insertRow(row)
            self._font_table.setItem(row, 0, QTableWidgetItem(name))
            self._font_table.setItem(row, 1, QTableWidgetItem(fnt.file_path))
            self._font_table.setItem(row, 2, QTableWidgetItem(str(fnt.point_size)))

    def _add_image(self):
        name, ok = QInputDialog.getText(self, tr("res.add_image", "Add Image"), tr("res.name", "Name:"))
        if not ok or not name:
            return
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("res.select_image", "Select Image"), "",
            tr("filter.images", "Images (*.png *.jpg *.bmp *.tga);;All Files (*)")
        )
        if not filepath:
            return
        self._res_mgr.add_image(name, filepath)
        self._populate()

    def _remove_image(self):
        row = self._img_table.currentRow()
        if row < 0:
            return
        name = self._img_table.item(row, 0).text()
        self._res_mgr.remove_image(name)
        self._populate()

    def _add_font(self):
        name, ok = QInputDialog.getText(self, tr("res.add_font", "Add Font"), tr("res.name", "Name:"))
        if not ok or not name:
            return
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("res.select_font", "Select Font"), "",
            tr("filter.fonts", "Font Files (*.txt *.font);;All Files (*)")
        )
        if not filepath:
            return
        self._res_mgr.add_font(name, filepath)
        self._populate()

    def _remove_font(self):
        row = self._font_table.currentRow()
        if row < 0:
            return
        name = self._font_table.item(row, 0).text()
        self._res_mgr.remove_font(name)
        self._populate()
