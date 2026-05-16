# -*- coding: utf-8 -*-
"""
.NET Resource Manager
Parses resources.xml and provides resource lookups for C# mode.
"""
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class NetImageResource:
    id: str
    path: str
    full_path: str
    format: str = "png"
    cols: int = 1
    rows: int = 1


@dataclass
class NetFontResource:
    id: str
    path: str
    full_path: str


@dataclass
class NetSoundResource:
    id: str
    path: str


class NetResourceManager:
    _instance = None
    DEFAULT_RESOLUTION = "480x800"
    DEFAULT_LANGUAGE = "en"

    def __init__(self, content_path: str = None):
        self.content_path = content_path or ""
        self.images: Dict[str, NetImageResource] = {}
        self.fonts: Dict[str, NetFontResource] = {}
        self.sounds: Dict[str, NetSoundResource] = {}
        self._loaded = False
        self.resolution = self.DEFAULT_RESOLUTION
        self.language = self.DEFAULT_LANGUAGE

    @classmethod
    def instance(cls, content_path: str = None):
        if cls._instance is None:
            cls._instance = cls(content_path)
        elif content_path and cls._instance.content_path != content_path:
            cls._instance = cls(content_path)
        return cls._instance

    def set_resolution(self, resolution: str):
        self.resolution = resolution
        self._loaded = False

    def set_language(self, language: str):
        self.language = language
        self._loaded = False

    def load(self, resources_xml_path: str = None) -> bool:
        if self._loaded:
            return True
        
        if not resources_xml_path:
            resources_xml_path = os.path.join(self.content_path, "resources.xml")
        
        if not os.path.exists(resources_xml_path):
            return False
        
        try:
            tree = ET.parse(resources_xml_path)
            root = tree.getroot()
            
            self.images.clear()
            self.fonts.clear()
            self.sounds.clear()
            
            current_path = "images"
            current_id_prefix = ""
            
            for elem in root.iter():
                if elem.tag == "SetDefaults":
                    current_path = elem.get("path", "images")
                    current_id_prefix = elem.get("idprefix", "")
                elif elem.tag == "Image":
                    img_id = elem.get("id", "")
                    img_path = elem.get("path", "")
                    img_format = elem.get("format", "png")
                    img_cols = int(elem.get("cols", "1"))
                    img_rows = int(elem.get("rows", "1"))
                    language_specific = elem.get("languageSpecific", "")
                    
                    if img_id:
                        full_id = current_id_prefix + img_id
                        
                        if current_path == "images":
                            if language_specific:
                                full_path = os.path.join(
                                    self.content_path, "images", self.resolution, 
                                    self.language, img_path + "." + img_format
                                )
                                if not os.path.exists(full_path):
                                    full_path = os.path.join(
                                        self.content_path, "images", self.resolution,
                                        img_path + "." + img_format
                                    )
                            else:
                                full_path = os.path.join(
                                    self.content_path, "images", self.resolution,
                                    img_path + "." + img_format
                                )
                        else:
                            full_path = os.path.join(self.content_path, current_path, img_path + "." + img_format)
                        
                        self.images[full_id] = NetImageResource(
                            id=full_id,
                            path=img_path,
                            full_path=full_path,
                            format=img_format,
                            cols=img_cols,
                            rows=img_rows
                        )
                elif elem.tag == "Font":
                    font_id = elem.get("id", "")
                    font_path = elem.get("path", "")
                    
                    if font_id:
                        full_id = current_id_prefix + font_id
                        if current_path.startswith("Content/"):
                            actual_path = current_path.replace("Content/", "")
                        else:
                            actual_path = current_path
                        full_path = os.path.join(self.content_path, actual_path, font_path)
                        self.fonts[full_id] = NetFontResource(
                            id=full_id,
                            path=font_path,
                            full_path=full_path
                        )
                elif elem.tag == "Sound":
                    sound_id = elem.get("id", "")
                    sound_path = elem.get("path", "")
                    
                    if sound_id:
                        full_id = current_id_prefix + sound_id
                        self.sounds[full_id] = NetSoundResource(
                            id=full_id,
                            path=sound_path
                        )
            
            self._loaded = True
            return True
        except Exception as e:
            print(f"Error loading resources.xml: {e}")
            return False

    def get_image(self, image_id: str) -> Optional[NetImageResource]:
        if not self._loaded:
            self.load()
        return self.images.get(image_id)

    def get_font(self, font_id: str) -> Optional[NetFontResource]:
        if not self._loaded:
            self.load()
        return self.fonts.get(font_id)

    def get_sound(self, sound_id: str) -> Optional[NetSoundResource]:
        if not self._loaded:
            self.load()
        return self.sounds.get(sound_id)

    def get_all_images(self) -> List[str]:
        if not self._loaded:
            self.load()
        return sorted(self.images.keys())

    def get_all_fonts(self) -> List[str]:
        if not self._loaded:
            self.load()
        return sorted(self.fonts.keys())

    def get_all_sounds(self) -> List[str]:
        if not self._loaded:
            self.load()
        return sorted(self.sounds.keys())

    def resolve_image_path(self, image_id: str) -> Optional[str]:
        img = self.get_image(image_id)
        if img and os.path.exists(img.full_path):
            return img.full_path
        return None

    def is_atlas_resource(self, image_id: str) -> bool:
        atlas_prefixes = (
            "IMAGE_REANIM_", "IMAGE_SELECTORSCREEN_", "IMAGE_SEEDCHOOSER_",
            "IMAGE_ALMANAC_", "IMAGE_BLASTMARK", "IMAGE_ROCKSMALL", "IMAGE_DIRTBIG",
            "IMAGE_DIRTSMALL", "IMAGE_RAIN", "IMAGE_LANTERNSHINE", "IMAGE_AWARD",
            "IMAGE_VASE_", "IMAGE_IMITATERCLOUDS", "IMAGE_ZOMBOSS_", "IMAGE_BEGHOULED_"
        )
        return any(image_id.startswith(prefix) for prefix in atlas_prefixes)

    def get_resource_class(self, image_id: str) -> str:
        if self.is_atlas_resource(image_id):
            return "AtlasResources"
        return "Resources"

    def get_default_button_image(self) -> str:
        return "IMAGE_DIALOG"

    def get_default_font(self) -> str:
        return "FONT_DWARVENTODCRAFT12"


def get_net_resource_manager(content_path: str = None) -> NetResourceManager:
    return NetResourceManager.instance(content_path)
