# -*- coding: utf-8 -*-
import os
from core.qt_compat import (
    QDialog, QVBoxLayout, QWidget, Qt, QRect,
    QPainter, QColor, QPen, QBrush, QFont, QPixmap
)
from core.project import Project
from core.resource_manager import ResourceManager
from core.i18n import tr
from ui.canvas import _WIDGET_COLORS
from ui.dark_titlebar import set_transparent_titlebar
from ui.image_picker import (
    get_image_path, get_net_image_path, is_atlas_sub_image,
    get_atlas_sub_image_info, get_atlas_source_path,
    _PAK_DIR, _NET_CONTENT_DIR
)


class PreviewCanvas(QWidget):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._image_cache = {}

    def _load_pixmap(self, image_ref: str) -> QPixmap:
        if not image_ref:
            return None
        if image_ref in self._image_cache:
            return self._image_cache[image_ref]

        platform = self.project.settings.target_platform if self.project else "cpp"
        
        if platform == "csharp":
            if is_atlas_sub_image(image_ref):
                sub_info = get_atlas_sub_image_info(image_ref)
                if sub_info:
                    atlas_path = get_atlas_source_path(image_ref)
                    if atlas_path:
                        full_path = os.path.join(_NET_CONTENT_DIR, atlas_path)
                        if os.path.exists(full_path):
                            full_pixmap = QPixmap(full_path)
                            if not full_pixmap.isNull():
                                rect = QRect(sub_info["x"], sub_info["y"], sub_info["width"], sub_info["height"])
                                px = full_pixmap.copy(rect)
                                self._image_cache[image_ref] = px
                                return px
            
            net_rel_path = get_net_image_path(image_ref)
            if net_rel_path:
                if isinstance(net_rel_path, str):
                    full_path = os.path.join(_NET_CONTENT_DIR, net_rel_path)
                    if os.path.exists(full_path):
                        px = QPixmap(full_path)
                        if not px.isNull():
                            self._image_cache[image_ref] = px
                            return px
            
            net_name = image_ref
            if net_name.startswith("IMAGE_"):
                net_name = net_name[6:]
            
            net_resolutions = ["480x800", "800x480"]
            for resolution in net_resolutions:
                net_png_path = os.path.join(_NET_CONTENT_DIR, "images", resolution, f"{net_name}.png")
                if os.path.exists(net_png_path):
                    px = QPixmap(net_png_path)
                    if not px.isNull():
                        self._image_cache[image_ref] = px
                        return px
                
                net_jpg_path = os.path.join(_NET_CONTENT_DIR, "images", resolution, f"{net_name}.jpg")
                if os.path.exists(net_jpg_path):
                    px = QPixmap(net_jpg_path)
                    if not px.isNull():
                        self._image_cache[image_ref] = px
                        return px
        else:
            rel_path = get_image_path(image_ref)
            if rel_path:
                full_path = os.path.join(_PAK_DIR, rel_path)
                if os.path.exists(full_path):
                    px = QPixmap(full_path)
                    if not px.isNull():
                        self._image_cache[image_ref] = px
                        return px

            res_mgr = ResourceManager.instance()
            name = image_ref
            if name.startswith("IMAGE_"):
                name = name[6:].lower()
            img_res = res_mgr.get_image(name)
            if img_res:
                full_path = os.path.join(_PAK_DIR, img_res.file_path)
                if os.path.exists(full_path):
                    px = QPixmap(full_path)
                    if not px.isNull():
                        self._image_cache[image_ref] = px
                        return px

            direct_path = os.path.join(_PAK_DIR, "images", f"{name}.png")
            if os.path.exists(direct_path):
                px = QPixmap(direct_path)
                if not px.isNull():
                    self._image_cache[image_ref] = px
                    return px

        self._image_cache[image_ref] = None
        return None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        iface = self.project.current_interface
        if iface:
            bg_color_str = iface.settings.background_color
            bg_img_ref = iface.settings.background_image
            bg_stretch = iface.settings.background_stretch
        else:
            bg_color_str = ""
            bg_img_ref = ""
            bg_stretch = False

        if bg_color_str:
            parts = bg_color_str.split(",")
            try:
                r = int(parts[0].strip()) if len(parts) > 0 else 0
                g = int(parts[1].strip()) if len(parts) > 1 else 0
                b = int(parts[2].strip()) if len(parts) > 2 else 0
                painter.fillRect(self.rect(), QColor(r, g, b))
            except ValueError:
                painter.fillRect(self.rect(), QColor(0, 0, 0))
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0))

        if bg_img_ref:
            px = self._load_pixmap(bg_img_ref)
            if px and not px.isNull():
                if bg_stretch:
                    scaled = px.scaled(self.width(), self.height(), 
                                      Qt.AspectRatioMode.IgnoreAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
                    painter.drawPixmap(0, 0, scaled)
                else:
                    painter.drawPixmap(0, 0, px)

        for wid_id in self.project.root_widget_ids:
            self._draw_widget(painter, wid_id)

        painter.end()

    def _resolve_dynamic_size(self, value: int, img_px: QPixmap, is_width: bool) -> int:
        if value >= 0:
            return value
        if img_px is None or img_px.isNull():
            return 100 if is_width else 30
        img_size = img_px.width() if is_width else img_px.height()
        special_sizes = {
            -1: img_size,
            -2: img_size + 23,
            -3: img_size + 33,
            -4: img_size + 10,
            -5: img_size,
            -6: img_size,
            -7: img_size,
        }
        return special_sizes.get(value, img_size)

    def _resolve_dynamic_pos(self, value: int, img_px: QPixmap, is_x: bool) -> int:
        if value >= 0:
            return value
        iface = self.project.current_interface
        canvas_w = iface.settings.width if iface else 800
        canvas_h = iface.settings.height if iface else 600
        img_h = img_px.height() if img_px and not img_px.isNull() else 30
        if is_x:
            special_positions = {
                -7: canvas_w - 150,
                -6: 20,
            }
        else:
            special_positions = {
                -7: 455,
                -6: canvas_h - img_h - 35,
            }
        return special_positions.get(value, value)

    def _draw_widget(self, painter: QPainter, widget_id: str):
        w = self.project.get_widget(widget_id)
        if not w:
            return

        props = w.properties
        raw_x = props.get("mX", 0)
        raw_y = props.get("mY", 0)
        raw_width = props.get("mWidth", 100)
        raw_height = props.get("mHeight", 30)

        img_px = None
        for img_key in ["mButtonImage", "mComponentImage", "mUncheckedImage", "mTrackImage", "mImage"]:
            img_ref = props.get(img_key, "")
            if not img_ref and img_key == "mButtonImage" and w.class_name == "NewLawnButton":
                img_ref = props.get("mUniformImage", "")
            if img_ref:
                img_px = self._load_pixmap(img_ref)
                if img_px and not img_px.isNull():
                    break

        x = self._resolve_dynamic_pos(raw_x, img_px, True)
        y = self._resolve_dynamic_pos(raw_y, img_px, False)
        width = self._resolve_dynamic_size(raw_width, img_px, True)
        height = self._resolve_dynamic_size(raw_height, img_px, False)

        img_drawn = False
        if img_px and not img_px.isNull():
            stretch = False
            if w.class_name == "ImageBox":
                stretch = props.get("mStretch", False)
            
            if stretch:
                scaled = img_px.scaled(width, height, 
                                  Qt.AspectRatioMode.IgnoreAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
                painter.drawPixmap(x, y, scaled)
            else:
                scale_x = props.get("mScaleX", 1.0)
                scale_y = props.get("mScaleY", 1.0)
                if scale_x != 1.0 or scale_y != 1.0:
                    scaled = img_px.scaled(int(img_px.width() * scale_x),
                                      int(img_px.height() * scale_y),
                                      Qt.AspectRatioMode.IgnoreAspectRatio,
                                      Qt.TransformationMode.SmoothTransformation)
                    painter.drawPixmap(x, y, scaled)
                else:
                    painter.drawPixmap(x, y, img_px)
            img_drawn = True

        if not img_drawn:
            color = _WIDGET_COLORS.get(w.class_name, QColor(200, 200, 200, 80))
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor(80, 80, 80), 1))
            painter.drawRect(x, y, width, height)

        if w.class_name == "Label":
            text = props.get("mText", "")
            if text:
                font_color = props.get("mColor", "255,255,255")
                parts = font_color.split(",") if font_color else ["255", "255", "255"]
                r = int(parts[0].strip()) if len(parts) > 0 else 255
                g = int(parts[1].strip()) if len(parts) > 1 else 255
                b = int(parts[2].strip()) if len(parts) > 2 else 255
                painter.setPen(QPen(QColor(r, g, b), 1))
                font = QFont("Microsoft YaHei", 12)
                painter.setFont(font)
                justify = props.get("mJustify", "LEFT")
                align = Qt.AlignmentFlag.AlignLeft
                if justify == "CENTER":
                    align = Qt.AlignmentFlag.AlignHCenter
                elif justify == "RIGHT":
                    align = Qt.AlignmentFlag.AlignRight
                painter.drawText(QRect(x, y, width, height), 
                                align | Qt.AlignmentFlag.AlignVCenter | Qt.TextFlag.TextWordWrap, 
                                text)
        else:
            label = props.get("mLabel", "") or w.instance_name or w.class_name
            font = QFont("Microsoft YaHei", 9)
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(x + 4, y + 14, label)

        for child_id in w.children:
            self._draw_widget(painter, child_id)


class PreviewWindow(QDialog):
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        set_transparent_titlebar(self)
        self.setWindowTitle(tr("preview.title", "Preview"))
        iface = project.current_interface
        if iface:
            w = iface.settings.width
            h = iface.settings.height
        else:
            w, h = 800, 600
        self.resize(w + 20, h + 20)

        layout = QVBoxLayout(self)
        self._canvas = PreviewCanvas(project, self)
        self._canvas.setFixedSize(w, h)
        layout.addWidget(self._canvas)
