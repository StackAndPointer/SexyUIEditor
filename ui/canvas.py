# -*- coding: utf-8 -*-
import os
from PyQt6.QtWidgets import QWidget, QScrollArea
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QRect, QSize, QEvent
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPixmap, QMouseEvent, QWheelEvent
from core.project import Project, WidgetInstance
from core.component_registry import ComponentRegistry
from core.resource_manager import ResourceManager
from core.net_resources import get_net_resource_manager
from ui.image_picker import get_image_path, get_font_path, _PAK_DIR, _NET_CONTENT_DIR
from ui.image_picker import get_net_image_path, is_atlas_sub_image, get_atlas_sub_image_info, get_atlas_source_path

_WIDGET_COLORS = {
    "Widget": QColor(200, 200, 200, 80),
    "ButtonWidget": QColor(100, 149, 237, 100),
    "DialogButton": QColor(100, 149, 237, 100),
    "HyperlinkWidget": QColor(0, 191, 255, 100),
    "EditWidget": QColor(255, 255, 224, 100),
    "TextWidget": QColor(240, 240, 240, 100),
    "Label": QColor(240, 240, 240, 60),
    "ListWidget": QColor(230, 230, 250, 100),
    "ScrollbarWidget": QColor(192, 192, 192, 100),
    "Checkbox": QColor(144, 238, 144, 100),
    "Slider": QColor(255, 218, 185, 100),
    "Dialog": QColor(176, 196, 222, 120),
    "LawnDialog": QColor(176, 196, 222, 120),
    "LawnStoneButton": QColor(169, 169, 169, 100),
    "NewLawnButton": QColor(60, 179, 113, 100),
    "LawnEditWidget": QColor(255, 255, 224, 100),
    "ScrollbuttonWidget": QColor(192, 192, 192, 100),
    "GameButton": QColor(255, 165, 0, 100),
    "ImageBox": QColor(200, 200, 200, 60),
}


class _CanvasWidget(QWidget):
    def __init__(self, canvas, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def paintEvent(self, event):
        self.canvas._do_paint(self)

    def mousePressEvent(self, event):
        self.canvas._handle_mouse_press(event)

    def mouseMoveEvent(self, event):
        self.canvas._handle_mouse_move(event)

    def mouseReleaseEvent(self, event):
        self.canvas._handle_mouse_release(event)

    def _on_context_menu(self, pos):
        self.canvas._handle_context_menu(pos)


class DesignCanvas(QScrollArea):
    widget_selected = pyqtSignal(str)
    widget_moved = pyqtSignal(str, int, int)
    widget_resized = pyqtSignal(str, int, int)
    widget_context_menu = pyqtSignal(str, QPoint)

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self._selected_id = ""
        self._dragging = False
        self._resizing = False
        self._resize_handle = ""
        self._drag_start = QPoint()
        self._drag_orig_pos = QPoint()
        self._resize_orig_rect = QRect()
        self._grid_size = 10
        self._show_grid = True
        self._zoom = 1.0
        self._image_cache = {}

        self._inner = _CanvasWidget(self)
        self._inner.setMinimumSize(800, 600)
        self.setWidget(self._inner)
        self.setWidgetResizable(False)
        self.setAcceptDrops(True)

    def set_project(self, project: Project):
        self.project = project
        self._selected_id = ""
        self._image_cache = {}
        self.refresh()

    def refresh(self):
        self._image_cache = {}
        iface = self.project.current_interface
        if iface:
            w = iface.settings.width
            h = iface.settings.height
        else:
            w, h = 800, 600
        self._inner.setFixedSize(int(w * self._zoom), int(h * self._zoom))
        self._inner.update()

    def selected_widget_id(self) -> str:
        return self._selected_id

    def select_widget(self, widget_id: str):
        self._selected_id = widget_id
        self._inner.update()

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
                name = name[6:]
            img_res = res_mgr.get_image(name.lower())
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

    def _do_paint(self, widget):
        painter = QPainter(widget)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        iface = self.project.current_interface
        bg_color_str = iface.settings.background_color if iface else ""
        if bg_color_str:
            parts = bg_color_str.split(",")
            try:
                r = int(parts[0].strip()) if len(parts) > 0 else 48
                g = int(parts[1].strip()) if len(parts) > 1 else 48
                b = int(parts[2].strip()) if len(parts) > 2 else 48
                painter.fillRect(widget.rect(), QColor(r, g, b))
            except ValueError:
                painter.fillRect(widget.rect(), QColor(48, 48, 48))
        else:
            painter.fillRect(widget.rect(), QColor(48, 48, 48))

        bg_img_ref = iface.settings.background_image if iface else ""
        bg_stretch = iface.settings.background_stretch if iface else False
        if bg_img_ref:
            px = self._load_pixmap(bg_img_ref)
            if px and not px.isNull():
                if bg_stretch:
                    scaled = px.scaled(widget.size(), Qt.AspectRatioMode.IgnoreAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
                    painter.drawPixmap(0, 0, scaled)
                else:
                    painter.drawPixmap(0, 0, px)

        if self._show_grid:
            painter.setPen(QPen(QColor(60, 60, 60), 1))
            gs = int(self._grid_size * self._zoom)
            if gs > 0:
                for x in range(0, widget.width(), gs):
                    painter.drawLine(x, 0, x, widget.height())
                for y in range(0, widget.height(), gs):
                    painter.drawLine(0, y, widget.width(), y)

        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRect(0, 0, widget.width() - 1, widget.height() - 1)

        for wid_id in self.project.root_widget_ids:
            self._draw_widget(painter, wid_id)

        painter.end()

    def _draw_widget(self, painter: QPainter, widget_id: str):
        w = self.project.get_widget(widget_id)
        if not w:
            return

        props = w.properties
        x = int(props.get("mX", 0) * self._zoom)
        y = int(props.get("mY", 0) * self._zoom)
        width = int(props.get("mWidth", 100) * self._zoom)
        height = int(props.get("mHeight", 30) * self._zoom)

        img_drawn = False
        for img_key in ["mButtonImage", "mComponentImage", "mUncheckedImage", "mTrackImage", "mImage"]:
            img_ref = props.get(img_key, "")
            if not img_ref and img_key == "mButtonImage" and w.class_name == "NewLawnButton":
                img_ref = props.get("mUniformImage", "")
            if img_ref:
                px = self._load_pixmap(img_ref)
                if px and not px.isNull():
                    stretch = False
                    if w.class_name == "ImageBox":
                        stretch = props.get("mStretch", False)
                    
                    if stretch:
                        scaled = px.scaled(width, height, Qt.AspectRatioMode.IgnoreAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
                        painter.drawPixmap(x, y, scaled)
                    else:
                        scale_x = props.get("mScaleX", 1.0)
                        scale_y = props.get("mScaleY", 1.0)
                        if scale_x != 1.0 or scale_y != 1.0:
                            scaled = px.scaled(int(px.width() * scale_x * self._zoom),
                                              int(px.height() * scale_y * self._zoom),
                                              Qt.AspectRatioMode.IgnoreAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)
                            painter.drawPixmap(x, y, scaled)
                        else:
                            painter.drawPixmap(x, y, px)
                    img_drawn = True
                    break

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
                font = QFont("Microsoft YaHei", max(8, int(12 * self._zoom)))
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
            label = w.instance_name or w.class_name
            display_text = props.get("mLabel", "") or label
            font = QFont("Microsoft YaHei", max(8, int(9 * self._zoom)))
            painter.setFont(font)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawText(QRect(x + 2, y + 2, width - 4, height - 4),
                             Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                             display_text)

        class_font = QFont("Microsoft YaHei", max(7, int(7 * self._zoom)))
        painter.setFont(class_font)
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        painter.drawText(QRect(x + 2, y + height - int(12 * self._zoom), width - 4, int(10 * self._zoom)),
                         Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                         w.class_name)

        if w.id == self._selected_id:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(0, 120, 215), 2, Qt.PenStyle.DashLine))
            painter.drawRect(x - 1, y - 1, width + 2, height + 2)

            handle_size = 6
            handles = self._get_handles(x, y, width, height, handle_size)
            painter.setBrush(QBrush(QColor(0, 120, 215)))
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            for h in handles:
                painter.drawRect(h)

        for child_id in w.children:
            self._draw_widget(painter, child_id)

    def _get_handles(self, x, y, w, h, size) -> list:
        hs = size
        return [
            QRect(x - hs, y - hs, hs * 2, hs * 2),
            QRect(x + w - hs, y - hs, hs * 2, hs * 2),
            QRect(x - hs, y + h - hs, hs * 2, hs * 2),
            QRect(x + w - hs, y + h - hs, hs * 2, hs * 2),
            QRect(x + w // 2 - hs, y - hs, hs * 2, hs * 2),
            QRect(x + w // 2 - hs, y + h - hs, hs * 2, hs * 2),
            QRect(x - hs, y + h // 2 - hs, hs * 2, hs * 2),
            QRect(x + w - hs, y + h // 2 - hs, hs * 2, hs * 2),
        ]

    def _hit_test(self, pos: QPoint) -> str:
        for wid_id in reversed(self.project.root_widget_ids):
            result = self._hit_test_widget(pos, wid_id)
            if result:
                return result
        return ""

    def _hit_test_widget(self, pos: QPoint, widget_id: str) -> str:
        w = self.project.get_widget(widget_id)
        if not w:
            return ""
        for child_id in reversed(w.children):
            result = self._hit_test_widget(pos, child_id)
            if result:
                return result
        props = w.properties
        x = int(props.get("mX", 0) * self._zoom)
        y = int(props.get("mY", 0) * self._zoom)
        width = int(props.get("mWidth", 100) * self._zoom)
        height = int(props.get("mHeight", 30) * self._zoom)
        if QRect(x, y, width, height).contains(pos):
            return w.id
        return ""

    def _hit_handle(self, pos: QPoint) -> str:
        if not self._selected_id:
            return ""
        w = self.project.get_widget(self._selected_id)
        if not w:
            return ""
        props = w.properties
        x = int(props.get("mX", 0) * self._zoom)
        y = int(props.get("mY", 0) * self._zoom)
        width = int(props.get("mWidth", 100) * self._zoom)
        height = int(props.get("mHeight", 30) * self._zoom)
        handles = self._get_handles(x, y, width, height, 8)
        names = ["tl", "tr", "bl", "br", "tm", "bm", "ml", "mr"]
        for name, handle in zip(names, handles):
            if handle.contains(pos):
                return name
        return ""

    def _handle_mouse_press(self, event: QMouseEvent):
        if event.button() != Qt.MouseButton.LeftButton:
            return
        pos = event.position().toPoint()

        handle = self._hit_handle(pos)
        if handle:
            self._resizing = True
            self._resize_handle = handle
            self._drag_start = pos
            w = self.project.get_widget(self._selected_id)
            if w:
                self._resize_orig_rect = QRect(
                    int(w.properties.get("mX", 0)),
                    int(w.properties.get("mY", 0)),
                    int(w.properties.get("mWidth", 100)),
                    int(w.properties.get("mHeight", 30))
                )
            return

        hit = self._hit_test(pos)
        if hit:
            self._selected_id = hit
            self.widget_selected.emit(hit)
            self._dragging = True
            self._drag_start = pos
            w = self.project.get_widget(hit)
            if w:
                self._drag_orig_pos = QPoint(
                    int(w.properties.get("mX", 0)),
                    int(w.properties.get("mY", 0))
                )
        else:
            self._selected_id = ""
            self.widget_selected.emit("")
        self._inner.update()

    def _handle_mouse_move(self, event: QMouseEvent):
        pos = event.position().toPoint()

        if self._dragging and self._selected_id:
            dx = pos.x() - self._drag_start.x()
            dy = pos.y() - self._drag_start.y()
            new_x = int((self._drag_orig_pos.x() * self._zoom + dx) / self._zoom)
            new_y = int((self._drag_orig_pos.y() * self._zoom + dy) / self._zoom)
            new_x = (new_x // self._grid_size) * self._grid_size
            new_y = (new_y // self._grid_size) * self._grid_size
            w = self.project.get_widget(self._selected_id)
            if w:
                w.properties["mX"] = new_x
                w.properties["mY"] = new_y
                self._inner.update()

        elif self._resizing and self._selected_id:
            dx = int((pos.x() - self._drag_start.x()) / self._zoom)
            dy = int((pos.y() - self._drag_start.y()) / self._zoom)
            r = self._resize_orig_rect
            new_rect = self._apply_resize(r, dx, dy)
            w = self.project.get_widget(self._selected_id)
            if w:
                w.properties["mX"] = new_rect.x()
                w.properties["mY"] = new_rect.y()
                w.properties["mWidth"] = max(20, new_rect.width())
                w.properties["mHeight"] = max(20, new_rect.height())
                self._inner.update()

    def _handle_mouse_release(self, event: QMouseEvent):
        if self._dragging and self._selected_id:
            w = self.project.get_widget(self._selected_id)
            if w:
                self.widget_moved.emit(
                    self._selected_id,
                    int(w.properties.get("mX", 0)),
                    int(w.properties.get("mY", 0))
                )
        elif self._resizing and self._selected_id:
            w = self.project.get_widget(self._selected_id)
            if w:
                self.widget_resized.emit(
                    self._selected_id,
                    int(w.properties.get("mWidth", 100)),
                    int(w.properties.get("mHeight", 30))
                )
        self._dragging = False
        self._resizing = False

    def _handle_context_menu(self, pos: QPoint):
        hit = self._hit_test(pos)
        if hit:
            global_pos = self._inner.mapToGlobal(pos)
            self.widget_context_menu.emit(hit, global_pos)

    def _apply_resize(self, orig: QRect, dx: int, dy: int) -> QRect:
        r = QRect(orig)
        h = self._resize_handle
        if "l" in h:
            r.setLeft(r.left() + dx)
        if "r" in h:
            r.setRight(r.right() + dx)
        if "t" in h:
            r.setTop(r.top() + dy)
        if "b" in h:
            r.setBottom(r.bottom() + dy)
        if r.width() < 20:
            if "l" in h:
                r.setLeft(r.right() - 20)
            else:
                r.setRight(r.left() + 20)
        if r.height() < 20:
            if "t" in h:
                r.setTop(r.bottom() - 20)
            else:
                r.setBottom(r.top() + 20)
        return r

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        class_name = event.mimeData().text()
        pos = self._inner.mapFrom(self, event.position().toPoint())
        x = int(pos.x() / self._zoom)
        y = int(pos.y() / self._zoom)
        x = (x // self._grid_size) * self._grid_size
        y = (y // self._grid_size) * self._grid_size
        from ui.main_window import MainWindow
        main_win = self.window()
        if isinstance(main_win, MainWindow):
            main_win._on_widget_added(class_name, x, y)
        event.acceptProposedAction()

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self._zoom = min(3.0, self._zoom + 0.1)
            else:
                self._zoom = max(0.3, self._zoom - 0.1)
            self.refresh()
        else:
            super().wheelEvent(event)
