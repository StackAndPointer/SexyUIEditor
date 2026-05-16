# -*- coding: utf-8 -*-
"""
Resource Group Parser Module
Parses resources.xml to build image-to-resource-group mappings for deferred loading.
"""
import xml.etree.ElementTree as ET
from typing import Dict, Optional
import os

_DELAY_LOAD_PREFIX = "DelayLoad_"

_image_to_group_cache: Dict[str, str] = {}
_resources_path: Optional[str] = None


def parse_resources_xml(resources_path: str) -> Dict[str, str]:
    global _image_to_group_cache, _resources_path
    
    if _resources_path == resources_path and _image_to_group_cache:
        return _image_to_group_cache
    
    _resources_path = resources_path
    _image_to_group_cache = {}
    
    if not os.path.exists(resources_path):
        return _image_to_group_cache
    
    try:
        tree = ET.parse(resources_path)
        root = tree.getroot()
        
        for resources_elem in root.findall("Resources"):
            group_id = resources_elem.get("id", "")
            if not group_id.startswith(_DELAY_LOAD_PREFIX):
                continue
            
            idprefix = ""
            for set_defaults in resources_elem.findall("SetDefaults"):
                idprefix = set_defaults.get("idprefix", "")
                break
            
            for image_elem in resources_elem.findall("Image"):
                image_id = image_elem.get("id", "")
                if image_id:
                    full_id = idprefix + image_id
                    _image_to_group_cache[full_id] = group_id
    
    except Exception as e:
        print(f"Error parsing resources.xml: {e}")
    
    return _image_to_group_cache


def get_resource_group_for_image(image_id: str, resources_path: str) -> Optional[str]:
    if not image_id:
        return None
    
    if not image_id.startswith("IMAGE_"):
        image_id = "IMAGE_" + image_id
    
    mapping = parse_resources_xml(resources_path)
    return mapping.get(image_id)


def get_delay_load_call(image_id: str, resources_path: str) -> Optional[str]:
    group_name = get_resource_group_for_image(image_id, resources_path)
    if group_name:
        return f'mApp.DelayLoadBackgroundResource("{group_name}");'
    return None
