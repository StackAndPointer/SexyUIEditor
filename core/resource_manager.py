# -*- coding: utf-8 -*-
import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ImageResource:
    name: str
    file_path: str
    width: int = 0
    height: int = 0
    rows: int = 1
    cols: int = 1


@dataclass
class FontResource:
    name: str
    file_path: str
    point_size: int = 12


class ResourceManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._images: Dict[str, ImageResource] = {}
        self._fonts: Dict[str, FontResource] = {}
        self._resource_dir: str = ""
        self._image_prefix = "IMAGE_"
        self._font_prefix = "FONT_"

    def set_resource_dir(self, path: str):
        self._resource_dir = path

    def add_image(self, name: str, file_path: str, rows: int = 1, cols: int = 1) -> ImageResource:
        res = ImageResource(name=name, file_path=file_path, rows=rows, cols=cols)
        self._images[name] = res
        return res

    def add_font(self, name: str, file_path: str, point_size: int = 12) -> FontResource:
        res = FontResource(name=name, file_path=file_path, point_size=point_size)
        self._fonts[name] = res
        return res

    def remove_image(self, name: str):
        self._images.pop(name, None)

    def remove_font(self, name: str):
        self._fonts.pop(name, None)

    def get_image(self, name: str) -> Optional[ImageResource]:
        return self._images.get(name)

    def get_font(self, name: str) -> Optional[FontResource]:
        return self._fonts.get(name)

    def all_images(self) -> Dict[str, ImageResource]:
        return dict(self._images)

    def all_fonts(self) -> Dict[str, FontResource]:
        return dict(self._fonts)

    def image_names(self) -> List[str]:
        return list(self._images.keys())

    def font_names(self) -> List[str]:
        return list(self._fonts.keys())

    def generate_image_code(self, name: str) -> str:
        img = self._images.get(name)
        if not img:
            return f"// Image resource '{name}' not found"
        lines = [
            f"// Image: {name}",
            f"// File: {img.file_path}",
            f"extern Image* {self._image_prefix}{name.upper()};",
        ]
        return "\n".join(lines)

    def generate_font_code(self, name: str) -> str:
        fnt = self._fonts.get(name)
        if not fnt:
            return f"// Font resource '{name}' not found"
        lines = [
            f"// Font: {name}",
            f"// File: {fnt.file_path}",
            f"extern _Font* {self._font_prefix}{name.upper()};",
        ]
        return "\n".join(lines)

    def generate_load_code(self) -> str:
        lines = ["// Load image resources"]
        for name, img in self._images.items():
            lines.append(f'{self._image_prefix}{name.upper()} = mApp->GetImage("{img.file_path}");')
        lines.append("")
        lines.append("// Load font resources")
        for name, fnt in self._fonts.items():
            lines.append(
                f'{self._font_prefix}{name.upper()} = new ImageFont(mApp, "{fnt.file_path}");'
            )
        return "\n".join(lines)

    def save(self, filepath: str):
        data = {
            "images": [
                {"name": i.name, "file_path": i.file_path, "rows": i.rows, "cols": i.cols}
                for i in self._images.values()
            ],
            "fonts": [
                {"name": f.name, "file_path": f.file_path, "point_size": f.point_size}
                for f in self._fonts.values()
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            return
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._images.clear()
        for img in data.get("images", []):
            self.add_image(img["name"], img["file_path"], img.get("rows", 1), img.get("cols", 1))
        self._fonts.clear()
        for fnt in data.get("fonts", []):
            self.add_font(fnt["name"], fnt["file_path"], fnt.get("point_size", 12))
