# -*- coding: utf-8 -*-
import hashlib
import os
from typing import Dict, Tuple, Optional
from core.project import Project
from core.code_generator import CodeGenerator
from core.code_parser import CodeParser


class CodeSyncManager:
    def __init__(self, project: Project):
        self._project = project
        self._code_gen = CodeGenerator.instance()
        self._file_hashes: Dict[str, str] = {}

    def sync_from_source(self) -> Tuple[bool, str]:
        settings = self._project.settings
        if not settings.source_header and not settings.source_cpp:
            return False, "未关联源文件"

        try:
            user_code = CodeParser.extract_from_files(
                settings.source_header,
                settings.source_cpp
            )

            self._project.user_code = user_code
            self._project.modified = True

            return True, "同步成功"
        except Exception as e:
            return False, f"同步失败: {e}"

    def sync_to_source(self, header_path: str, cpp_path: str) -> Tuple[bool, str]:
        try:
            header = self._code_gen.generate_header(self._project)
            cpp = self._code_gen.generate_cpp(self._project)

            os.makedirs(os.path.dirname(header_path) or '.', exist_ok=True)

            with open(header_path, 'w', encoding='utf-8') as f:
                f.write(header)
            with open(cpp_path, 'w', encoding='utf-8') as f:
                f.write(cpp)

            self._project.settings.source_header = header_path
            self._project.settings.source_cpp = cpp_path

            self._update_file_hashes()

            return True, "生成成功"
        except Exception as e:
            return False, f"生成失败: {e}"

    def check_file_changes(self) -> bool:
        iface = self._project.current_interface
        if not iface:
            return False
        for path in [iface.settings.source_header,
                     iface.settings.source_cpp]:
            if path and os.path.exists(path):
                current_hash = self._compute_file_hash(path)
                if path in self._file_hashes:
                    if current_hash != self._file_hashes[path]:
                        return True
                self._file_hashes[path] = current_hash
        return False

    def _compute_file_hash(self, path: str) -> str:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()

    def _update_file_hashes(self):
        iface = self._project.current_interface
        if not iface:
            return
        for path in [iface.settings.source_header,
                     iface.settings.source_cpp]:
            if path and os.path.exists(path):
                self._file_hashes[path] = self._compute_file_hash(path)

    def get_file_hash(self, path: str) -> Optional[str]:
        return self._file_hashes.get(path)
