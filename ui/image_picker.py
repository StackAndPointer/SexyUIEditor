# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QListWidgetItem, QLabel, QPushButton, QSplitter, QWidget,
    QAbstractItemView, QScrollArea, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt6.QtGui import QPixmap, QImage, QIcon, QPainter
from core.i18n import tr
import os
import xml.etree.ElementTree as ET
import json

_PAK_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pak")
_IMAGES_DIR = os.path.join(_PAK_DIR, "images")
_DATA_DIR = os.path.join(_PAK_DIR, "data")
_RESOURCES_XML = os.path.join(_PAK_DIR, "properties", "resources.xml")

_NET_CONTENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Content")
_NET_RESOURCES_XML = os.path.join(_NET_CONTENT_DIR, "resources.xml")
_NET_ATLAS_DEF = os.path.join(_NET_CONTENT_DIR, "atlas_definitions.json")
_NET_RESOLUTION = "480x800"

_NET_ATLAS_INFO = {}

def _load_atlas_definitions():
    global _NET_ATLAS_INFO
    if os.path.exists(_NET_ATLAS_DEF):
        try:
            with open(_NET_ATLAS_DEF, 'r', encoding='utf-8') as f:
                _NET_ATLAS_INFO = json.load(f)
        except Exception as e:
            print(f"Error loading atlas definitions: {e}")
            _NET_ATLAS_INFO = {}

_load_atlas_definitions()


def _parse_resources_xml() -> tuple:
    images = {}
    fonts = {}
    resource_groups = {}
    if not os.path.exists(_RESOURCES_XML):
        return images, fonts, resource_groups
    
    try:
        tree = ET.parse(_RESOURCES_XML)
        root = tree.getroot()
        
        for resources in root.findall('Resources'):
            current_path = "images"
            current_prefix = "IMAGE_"
            group_id = resources.get('id', '')
            
            for elem in resources:
                if elem.tag == 'SetDefaults':
                    current_path = elem.get('path', 'images')
                    current_prefix = elem.get('idprefix', 'IMAGE_')
                elif elem.tag == 'Image':
                    img_id = elem.get('id')
                    img_path = elem.get('path')
                    if img_id and img_path:
                        if current_prefix and not img_id.startswith(current_prefix):
                            full_id = current_prefix + img_id
                        else:
                            full_id = img_id
                        
                        if group_id and group_id not in ('Init', 'LoaderBar', 'LoadingFonts', 'LoadingImages'):
                            resource_groups[full_id] = group_id
                        
                        for ext in ['.png', '.jpg', '.gif', '']:
                            if ext:
                                full_path = os.path.join(current_path, img_path + ext)
                            else:
                                full_path = os.path.join(current_path, img_path)
                            test_path = os.path.join(_PAK_DIR, full_path)
                            if os.path.exists(test_path):
                                images[full_id] = full_path
                                break
                        else:
                            images[full_id] = os.path.join(current_path, img_path + '.png')
                elif elem.tag == 'Font':
                    font_id = elem.get('id')
                    font_path = elem.get('path')
                    if font_id and font_path:
                        full_id = current_prefix + font_id
                        full_path = os.path.join(current_path, font_path)
                        fonts[full_id] = full_path
                        
                        base_path = font_path.rsplit('.', 1)[0] if '.' in font_path else font_path
                        for ext in ['.png', '.gif', '.jpg']:
                            img_path = os.path.join(current_path, base_path + ext)
                            test_path = os.path.join(_PAK_DIR, img_path)
                            if os.path.exists(test_path):
                                images[full_id] = img_path
                                break
        
        return images, fonts, resource_groups
    except Exception as e:
        print(f"Error parsing resources.xml: {e}")
        return images, fonts, resource_groups


def _parse_net_resources_xml() -> tuple:
    images = {}
    fonts = {}
    resource_groups = {}
    
    if not os.path.exists(_NET_RESOURCES_XML):
        return images, fonts, resource_groups
    
    try:
        tree = ET.parse(_NET_RESOURCES_XML)
        root = tree.getroot()
        
        for resources in root.findall('Resources'):
            current_path = "images"
            current_prefix = "IMAGE_"
            group_id = resources.get('id', '')
            
            for elem in resources:
                if elem.tag == 'SetDefaults':
                    current_path = elem.get('path', 'images')
                    current_prefix = elem.get('idprefix', 'IMAGE_')
                elif elem.tag == 'Image':
                    img_id = elem.get('id')
                    img_path = elem.get('path')
                    img_format = elem.get('format', 'png')
                    if img_id and img_path:
                        if current_prefix and not img_id.startswith(current_prefix):
                            full_id = current_prefix + img_id
                        else:
                            full_id = img_id
                        
                        if group_id and group_id not in ('Init', 'LoaderBar', 'LoadingFonts', 'LoadingImages'):
                            resource_groups[full_id] = group_id
                        
                        if current_path == "images":
                            full_path = os.path.join("images", _NET_RESOLUTION, f"{img_path}.{img_format}")
                        else:
                            full_path = os.path.join(current_path, f"{img_path}.{img_format}")
                        
                        test_path = os.path.join(_NET_CONTENT_DIR, full_path)
                        if os.path.exists(test_path):
                            images[full_id] = full_path
                        else:
                            images[full_id] = full_path
                            
                elif elem.tag == 'Font':
                    font_id = elem.get('id')
                    font_path = elem.get('path')
                    if font_id and font_path:
                        full_id = current_prefix + font_id
                        if current_path.startswith("Content/"):
                            actual_path = current_path.replace("Content/", "")
                        else:
                            actual_path = current_path
                        full_path = os.path.join(actual_path, font_path)
                        fonts[full_id] = full_path
        
        images_dir = os.path.join(_NET_CONTENT_DIR, "images", _NET_RESOLUTION)
        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                filepath = os.path.join(images_dir, filename)
                if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.gif')):
                    base_name = os.path.splitext(filename)[0]
                    img_id = f"IMAGE_{base_name.upper()}"
                    if img_id not in images:
                        rel_path = os.path.join("images", _NET_RESOLUTION, filename)
                        images[img_id] = rel_path
        
        for atlas_name, atlas_data in _NET_ATLAS_INFO.items():
            if "sub_images" in atlas_data:
                for sub_name, sub_info in atlas_data["sub_images"].items():
                    images[sub_name] = {
                        "atlas": atlas_name,
                        "x": sub_info["x"],
                        "y": sub_info["y"],
                        "width": sub_info["width"],
                        "height": sub_info["height"]
                    }
        
        return images, fonts, resource_groups
    except Exception as e:
        print(f"Error parsing .NET resources.xml: {e}")
        return images, fonts, resource_groups


_IMAGE_MAP, _FONT_MAP, _RESOURCE_GROUPS = _parse_resources_xml()
_NET_IMAGE_MAP, _NET_FONT_MAP, _NET_RESOURCE_GROUPS = _parse_net_resources_xml()

IMAGE_FILE_MAP = _IMAGE_MAP
FONT_FILE_MAP = _FONT_MAP
IMAGE_RESOURCE_GROUPS = _RESOURCE_GROUPS

NET_IMAGE_FILE_MAP = _NET_IMAGE_MAP
NET_FONT_FILE_MAP = _NET_FONT_MAP

PVZ_IMAGES = sorted(IMAGE_FILE_MAP.keys())
PVZ_FONTS = sorted(FONT_FILE_MAP.keys())

NET_IMAGES = sorted(NET_IMAGE_FILE_MAP.keys())
NET_FONTS = sorted(NET_FONT_FILE_MAP.keys())


def get_image_path(image_name: str) -> str:
    if image_name in IMAGE_FILE_MAP:
        return IMAGE_FILE_MAP[image_name]
    return ""


def get_font_path(font_name: str) -> str:
    if font_name in FONT_FILE_MAP:
        txt_path = FONT_FILE_MAP[font_name]
        base_path = txt_path.rsplit('.', 1)[0] if '.' in txt_path else txt_path
        base_name = os.path.basename(base_path)
        dir_path = os.path.dirname(base_path)
        
        for ext in ['.png', '.gif', '.jpg']:
            img_path = os.path.join(dir_path, base_name + ext)
            test_path = os.path.join(_PAK_DIR, img_path)
            if os.path.exists(test_path):
                return img_path
        
        for ext in ['.png', '.gif', '.jpg']:
            img_path = os.path.join(dir_path, '_' + base_name + ext)
            test_path = os.path.join(_PAK_DIR, img_path)
            if os.path.exists(test_path):
                return img_path
        
        return txt_path
    return ""


def get_net_image_path(image_name: str):
    if image_name in NET_IMAGE_FILE_MAP:
        return NET_IMAGE_FILE_MAP[image_name]
    return ""


def get_net_font_path(font_name: str) -> str:
    if font_name in NET_FONT_FILE_MAP:
        return NET_FONT_FILE_MAP[font_name]
    return ""


def get_resource_group(image_name: str) -> str:
    return IMAGE_RESOURCE_GROUPS.get(image_name, "")


def is_atlas_source_image(image_name: str) -> bool:
    return image_name in _NET_ATLAS_INFO


def get_atlas_sub_images(atlas_name: str) -> list:
    if atlas_name in _NET_ATLAS_INFO:
        sub_images = _NET_ATLAS_INFO[atlas_name].get("sub_images", {})
        return sorted(sub_images.keys())
    return []


def is_atlas_sub_image(image_name: str) -> bool:
    if image_name in NET_IMAGE_FILE_MAP:
        info = NET_IMAGE_FILE_MAP[image_name]
        return isinstance(info, dict) and "atlas" in info
    return False


def get_atlas_sub_image_info(image_name: str) -> dict:
    if image_name in NET_IMAGE_FILE_MAP:
        info = NET_IMAGE_FILE_MAP[image_name]
        if isinstance(info, dict) and "atlas" in info:
            return info
    return None


def get_atlas_source_path(image_name: str) -> str:
    info = get_atlas_sub_image_info(image_name)
    if info:
        atlas_name = info["atlas"]
        if atlas_name in NET_IMAGE_FILE_MAP:
            atlas_path = NET_IMAGE_FILE_MAP[atlas_name]
            if isinstance(atlas_path, str):
                return atlas_path
    return ""


class ImagePickerDialog(QDialog):
    ROLE_ATLAS = "atlas"
    ROLE_SUB_IMAGE = "sub_image"
    ROLE_NORMAL = "normal"
    
    def __init__(self, current_value: str = "", resource_type: str = "image", parent=None, platform: str = "cpp"):
        super().__init__(parent)
        self._current_value = current_value
        self._resource_type = resource_type
        self._platform = platform
        self._selected_value = ""
        self._preview_cache = {}
        self._original_pixmap = None
        self._expanded_atlases = set()
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(tr("image_picker.title", "Select Resource"))
        self.setMinimumSize(700, 500)
        self.resize(800, 600)

        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_label = QLabel(tr("image_picker.search", "Search:"))
        self._search_edit = QLineEdit()
        self._search_edit.setPlaceholderText(tr("image_picker.search_hint", "Type to filter..."))
        self._search_edit.textChanged.connect(self._on_search)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self._search_edit)
        layout.addLayout(search_layout)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)

        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.itemDoubleClicked.connect(self._on_item_double_clicked)
        self._list.setIconSize(QSize(32, 32))
        list_layout.addWidget(self._list)

        splitter.addWidget(list_widget)

        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(8, 8, 8, 8)

        preview_label = QLabel(tr("image_picker.preview", "Preview"))
        preview_label.setStyleSheet("font-weight: bold;")
        preview_layout.addWidget(preview_label)

        self._preview_scroll = QScrollArea()
        self._preview_scroll.setWidgetResizable(True)
        self._preview_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_scroll.setStyleSheet("QScrollArea { background: #2a2a2a; border: 1px solid #555; }")

        self._preview_image = QLabel()
        self._preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_image.setStyleSheet("background: transparent;")
        self._preview_scroll.setWidget(self._preview_image)
        preview_layout.addWidget(self._preview_scroll, 1)

        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel(tr("image_picker.zoom", "Zoom:")))
        self._zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self._zoom_slider.setRange(25, 400)
        self._zoom_slider.setValue(100)
        self._zoom_slider.valueChanged.connect(self._on_zoom_changed)
        zoom_layout.addWidget(self._zoom_slider)
        self._zoom_label = QLabel("100%")
        self._zoom_label.setMinimumWidth(50)
        zoom_layout.addWidget(self._zoom_label)
        preview_layout.addLayout(zoom_layout)

        self._preview_name = QLabel()
        self._preview_name.setWordWrap(True)
        self._preview_name.setStyleSheet("font-family: monospace; font-size: 11px; color: #888;")
        preview_layout.addWidget(self._preview_name)

        self._preview_info = QLabel()
        self._preview_info.setWordWrap(True)
        preview_layout.addWidget(self._preview_info)

        splitter.addWidget(preview_widget)

        splitter.setSizes([400, 300])
        layout.addWidget(splitter)

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._ok_button = QPushButton(tr("button.ok", "OK"))
        self._ok_button.clicked.connect(self._on_ok)
        self._ok_button.setDefault(True)

        self._cancel_button = QPushButton(tr("button.cancel", "Cancel"))
        self._cancel_button.clicked.connect(self.reject)

        self._clear_button = QPushButton(tr("button.clear", "Clear"))
        self._clear_button.clicked.connect(self._on_clear)

        button_layout.addWidget(self._clear_button)
        button_layout.addWidget(self._cancel_button)
        button_layout.addWidget(self._ok_button)
        layout.addLayout(button_layout)

        self._load_items()

    def _load_items(self):
        if self._platform == "csharp":
            if self._resource_type == "image":
                self._all_items = NET_IMAGES
            else:
                self._all_items = NET_FONTS
        else:
            if self._resource_type == "image":
                self._all_items = PVZ_IMAGES
            else:
                self._all_items = PVZ_FONTS
        self._filter_items("")

    def _filter_items(self, filter_text: str):
        self._list.clear()
        filter_lower = filter_text.lower()

        if self._platform == "csharp" and self._resource_type == "image":
            atlas_items = []
            normal_items = []
            
            for item_name in self._all_items:
                if is_atlas_source_image(item_name):
                    atlas_items.append(item_name)
                elif not is_atlas_sub_image(item_name):
                    normal_items.append(item_name)
            
            for item_name in normal_items:
                if filter_lower and filter_lower not in item_name.lower():
                    continue
                list_item = QListWidgetItem(item_name)
                list_item.setData(Qt.ItemDataRole.UserRole, self.ROLE_NORMAL)
                list_item.setData(Qt.ItemDataRole.UserRole + 1, item_name)
                icon = self._get_icon(item_name)
                if icon:
                    list_item.setIcon(icon)
                if item_name == self._current_value:
                    list_item.setSelected(True)
                self._list.addItem(list_item)
            
            for atlas_name in atlas_items:
                if filter_lower and filter_lower not in atlas_name.lower():
                    sub_images = get_atlas_sub_images(atlas_name)
                    if not any(filter_lower in si.lower() for si in sub_images):
                        continue
                    
                    if atlas_name in self._expanded_atlases:
                        self._add_atlas_item(atlas_name, filter_lower)
                else:
                    self._add_atlas_item(atlas_name, filter_lower)
        else:
            for item_name in self._all_items:
                if filter_lower and filter_lower not in item_name.lower():
                    continue
                list_item = QListWidgetItem(item_name)
                list_item.setData(Qt.ItemDataRole.UserRole, self.ROLE_NORMAL)
                list_item.setData(Qt.ItemDataRole.UserRole + 1, item_name)
                icon = self._get_icon(item_name)
                if icon:
                    list_item.setIcon(icon)
                if item_name == self._current_value:
                    list_item.setSelected(True)
                self._list.addItem(list_item)

        if self._current_value:
            items = self._list.findItems(self._current_value, Qt.MatchFlag.MatchExactly)
            if items:
                self._list.setCurrentItem(items[0])
                self._list.scrollToItem(items[0])

    def _add_atlas_item(self, atlas_name: str, filter_lower: str):
        is_expanded = atlas_name in self._expanded_atlases
        prefix = "▼ " if is_expanded else "▶ "
        
        list_item = QListWidgetItem(prefix + atlas_name)
        list_item.setData(Qt.ItemDataRole.UserRole, self.ROLE_ATLAS)
        list_item.setData(Qt.ItemDataRole.UserRole + 1, atlas_name)
        list_item.setForeground(Qt.GlobalColor.cyan)
        icon = self._get_icon(atlas_name)
        if icon:
            list_item.setIcon(icon)
        self._list.addItem(list_item)
        
        if is_expanded:
            sub_images = get_atlas_sub_images(atlas_name)
            for sub_name in sub_images:
                if filter_lower and filter_lower not in sub_name.lower():
                    continue
                sub_item = QListWidgetItem("    " + sub_name)
                sub_item.setData(Qt.ItemDataRole.UserRole, self.ROLE_SUB_IMAGE)
                sub_item.setData(Qt.ItemDataRole.UserRole + 1, sub_name)
                sub_item.setForeground(Qt.GlobalColor.lightGray)
                icon = self._get_icon(sub_name)
                if icon:
                    sub_item.setIcon(icon)
                if sub_name == self._current_value:
                    sub_item.setSelected(True)
                self._list.addItem(sub_item)

    def _get_icon(self, name: str) -> QIcon:
        if name in self._preview_cache:
            return self._preview_cache[name]
        
        pixmap = self._get_pixmap_for_item(name)
        if pixmap and not pixmap.isNull():
            scaled = pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            icon = QIcon(scaled)
            self._preview_cache[name] = icon
            return icon
        return QIcon()

    def _get_pixmap_for_item(self, name: str) -> QPixmap:
        if self._platform == "csharp":
            if self._resource_type == "image":
                rel_path = get_net_image_path(name)
                if isinstance(rel_path, dict) and "atlas" in rel_path:
                    atlas_path = get_atlas_source_path(name)
                    if atlas_path:
                        full_path = os.path.join(_NET_CONTENT_DIR, atlas_path)
                        if os.path.exists(full_path):
                            full_pixmap = QPixmap(full_path)
                            if not full_pixmap.isNull():
                                rect = QRect(rel_path["x"], rel_path["y"], rel_path["width"], rel_path["height"])
                                return full_pixmap.copy(rect)
                elif rel_path:
                    path = os.path.join(_NET_CONTENT_DIR, rel_path)
                    if os.path.exists(path):
                        return QPixmap(path)
            else:
                rel_path = get_net_font_path(name)
                if rel_path:
                    path = os.path.join(_NET_CONTENT_DIR, rel_path)
                    if os.path.exists(path):
                        return QPixmap(path)
        else:
            if self._resource_type == "image":
                rel_path = get_image_path(name)
                if rel_path:
                    path = os.path.join(_PAK_DIR, rel_path)
                    if os.path.exists(path):
                        return QPixmap(path)
            else:
                rel_path = get_font_path(name)
                if rel_path:
                    path = os.path.join(_PAK_DIR, rel_path)
                    if os.path.exists(path):
                        return QPixmap(path)
        return QPixmap()

    def _on_search(self, text: str):
        self._filter_items(text)

    def _on_item_clicked(self, item: QListWidgetItem):
        role = item.data(Qt.ItemDataRole.UserRole)
        name = item.data(Qt.ItemDataRole.UserRole + 1)
        
        if role == self.ROLE_ATLAS:
            self._selected_value = ""
            self._update_preview_for_atlas(name)
        else:
            self._selected_value = name
            self._update_preview()

    def _on_item_double_clicked(self, item: QListWidgetItem):
        role = item.data(Qt.ItemDataRole.UserRole)
        name = item.data(Qt.ItemDataRole.UserRole + 1)
        
        if role == self.ROLE_ATLAS:
            scroll_pos = self._list.verticalScrollBar().value()
            if name in self._expanded_atlases:
                self._expanded_atlases.remove(name)
            else:
                self._expanded_atlases.add(name)
            self._filter_items(self._search_edit.text())
            self._list.verticalScrollBar().setValue(scroll_pos)
        elif role == self.ROLE_SUB_IMAGE or role == self.ROLE_NORMAL:
            self._selected_value = name
            self.accept()

    def _update_preview(self):
        self._preview_name.setText(self._selected_value)
        
        pixmap = self._get_pixmap_for_item(self._selected_value)
        if not pixmap.isNull():
            self._original_pixmap = pixmap
            self._apply_zoom()
            
            info_text = tr("image_picker.size", "Size: {}x{}").format(pixmap.width(), pixmap.height())
            if self._platform == "csharp" and is_atlas_sub_image(self._selected_value):
                sub_info = get_atlas_sub_image_info(self._selected_value)
                info_text += f" (Atlas: {sub_info['atlas']})"
            self._preview_info.setText(info_text)
            return
        
        self._original_pixmap = None
        self._preview_image.setText(tr("image_picker.no_preview", "No preview available"))
        self._preview_info.setText("")

    def _update_preview_for_atlas(self, atlas_name: str):
        self._preview_name.setText(atlas_name + " (Atlas)")
        
        rel_path = get_net_image_path(atlas_name)
        if rel_path and isinstance(rel_path, str):
            path = os.path.join(_NET_CONTENT_DIR, rel_path)
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    self._original_pixmap = pixmap
                    self._apply_zoom()
                    sub_count = len(get_atlas_sub_images(atlas_name))
                    self._preview_info.setText(tr("image_picker.atlas_info", "Atlas: {}x{}, {} sub-images").format(
                        pixmap.width(), pixmap.height(), sub_count))
                    return
        
        self._original_pixmap = None
        self._preview_image.setText(tr("image_picker.no_preview", "No preview available"))
        self._preview_info.setText("")

    def _on_zoom_changed(self, value: int):
        self._zoom_label.setText(f"{value}%")
        self._apply_zoom()

    def _apply_zoom(self):
        if self._original_pixmap is None:
            return
        
        zoom_factor = self._zoom_slider.value() / 100.0
        new_width = int(self._original_pixmap.width() * zoom_factor)
        new_height = int(self._original_pixmap.height() * zoom_factor)
        
        if new_width > 0 and new_height > 0:
            scaled = self._original_pixmap.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._preview_image.setPixmap(scaled)

    def _on_ok(self):
        self.accept()

    def _on_clear(self):
        self._selected_value = ""
        self.accept()

    def get_selected_value(self) -> str:
        return self._selected_value
