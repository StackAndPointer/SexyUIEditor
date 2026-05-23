# -*- coding: utf-8 -*-
import re
import os
from typing import Dict
from core.project import ProjectCode


class CodeParser:
    BLOCK_PATTERN = re.compile(
        r'//\s*\[\[\[(\w+)\]\]\]\s*\n(.*?)//\s*\[\[\[END_\1\]\]\]',
        re.DOTALL
    )

    @classmethod
    def extract_blocks(cls, source_code: str) -> Dict[str, str]:
        blocks = {}
        for match in cls.BLOCK_PATTERN.finditer(source_code):
            block_id = match.group(1)
            content = match.group(2)
            content = cls._clean_content(content)
            blocks[block_id] = content.strip()
        return blocks

    @classmethod
    def _clean_content(cls, content: str) -> str:
        lines = content.split('\n')
        cleaned = []
        skip_patterns = [
            '在此标记区域内添加你的成员声明',
            '在此添加自定义初始化代码',
            '在此添加清理代码',
            '在此添加自定义绘制代码',
            '在此添加自定义更新代码',
            '在此添加自定义函数实现',
            'Add custom member declarations here',
            'Add custom initialization code here',
            'Add custom cleanup code here',
            'Add custom drawing code here',
            'Add custom update code here',
            'Add custom function implementations here',
        ]
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('// 在此') or stripped.startswith('// 例如'):
                continue
            if stripped.startswith('// Add custom') or stripped.startswith('// Add '):
                for pattern in skip_patterns:
                    if pattern in stripped:
                        break
                else:
                    cleaned.append(line)
                continue
            if stripped.startswith('// ') and len(stripped) > 3:
                comment_text = stripped[3:]
                if any(pattern in comment_text for pattern in skip_patterns):
                    continue
            cleaned.append(line)
        return '\n'.join(cleaned)

    @classmethod
    def extract_from_files(cls, header_path: str, cpp_path: str) -> ProjectCode:
        code = ProjectCode()

        if header_path and os.path.exists(header_path):
            with open(header_path, 'r', encoding='utf-8') as f:
                header = f.read()
            blocks = cls.extract_blocks(header)
            code.header_includes = blocks.get('USER_INCLUDES', '')
            code.declarations = blocks.get('USER_DECLARATIONS', '')

        if cpp_path and os.path.exists(cpp_path):
            with open(cpp_path, 'r', encoding='utf-8') as f:
                cpp = f.read()
            blocks = cls.extract_blocks(cpp)

            code.cpp_includes = blocks.get('USER_INCLUDES', '')
            code.init_code = blocks.get('USER_INIT', '')
            code.destroy_code = blocks.get('USER_DESTROY', '')
            code.draw_code = blocks.get('USER_DRAW', '')
            code.update_code = blocks.get('USER_UPDATE', '')
            code.functions = blocks.get('USER_FUNCTIONS', '')

            for block_id, content in blocks.items():
                if block_id.startswith('HANDLER_') or \
                   block_id.startswith('EDIT_') or \
                   block_id.startswith('CHECKBOX_') or \
                   block_id.startswith('SLIDER_') or \
                   block_id.startswith('LIST_') or \
                   block_id.startswith('DIALOG_'):
                    code.event_handlers[block_id] = content

        return code

    @classmethod
    def extract_from_cs_file(cls, cs_path: str) -> ProjectCode:
        code = ProjectCode()

        if cs_path and os.path.exists(cs_path):
            with open(cs_path, 'r', encoding='utf-8') as f:
                cs_content = f.read()
            blocks = cls.extract_blocks(cs_content)

            code.cpp_includes = blocks.get('USER_INCLUDES', '')
            code.declarations = blocks.get('USER_DECLARATIONS', '')
            code.init_code = blocks.get('USER_INIT', '')
            code.destroy_code = blocks.get('USER_DESTROY', '')
            code.draw_code = blocks.get('USER_DRAW', '')
            code.update_code = blocks.get('USER_UPDATE', '')
            code.functions = blocks.get('USER_FUNCTIONS', '')

            for block_id, content in blocks.items():
                if block_id.startswith('HANDLER_') or \
                   block_id.startswith('EDIT_') or \
                   block_id.startswith('CHECKBOX_') or \
                   block_id.startswith('SLIDER_') or \
                   block_id.startswith('LIST_') or \
                   block_id.startswith('DIALOG_'):
                    code.event_handlers[block_id] = content

        return code
