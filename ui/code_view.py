# -*- coding: utf-8 -*-
import os
from core.qt_compat import (
    QDialog, QVBoxLayout, QTabWidget, QTextEdit, QPushButton, QHBoxLayout,
    QFileDialog, QComboBox, QLabel, QMessageBox, QFont, QSyntaxHighlighter,
    QTextCharFormat, QColor, QRegularExpression, QSettings
)
from core.i18n import tr
from ui.dark_titlebar import set_transparent_titlebar


class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self._formats = {}

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))
        keyword_format.setFontWeight(700)
        self._formats["keyword"] = keyword_format

        type_format = QTextCharFormat()
        type_format.setForeground(QColor(78, 201, 176))
        self._formats["type"] = type_format

        class_format = QTextCharFormat()
        class_format.setForeground(QColor(78, 201, 176))
        class_format.setFontWeight(700)
        self._formats["class"] = class_format

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))
        self._formats["string"] = string_format

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))
        self._formats["comment"] = comment_format

        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor(155, 155, 155))
        self._formats["preprocessor"] = preprocessor_format

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))
        self._formats["number"] = number_format

        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))
        self._formats["function"] = function_format

        constant_format = QTextCharFormat()
        constant_format.setForeground(QColor(86, 156, 214))
        self._formats["constant"] = constant_format

        self._patterns = [
            (r"//[^\n]*", "comment"),
            (r"/\*[\s\S]*?\*/", "comment"),
            (r"#[^\n]*", "preprocessor"),
            (r'"[^"\\]*(\\.[^"\\]*)*"', "string"),
            (r"'[^'\\]*(\\.[^'\\]*)*'", "string"),
            (r"\b(true|false|nullptr|TRUE|FALSE|NULL)\b", "constant"),
            (r"\b(virtual|override|final|const|static|extern|inline|explicit|friend|mutable|volatile|register|thread_local)\b", "keyword"),
            (r"\b(void|bool|int|float|double|char|wchar_t|auto|long|short|signed|unsigned|size_t|uint8_t|uint16_t|uint32_t|uint64_t|int8_t|int16_t|int32_t|int64_t)\b", "type"),
            (r"\b(class|struct|enum|union|namespace|using|typedef|template|typename|public|private|protected)\b", "class"),
            (r"\b(return|if|else|for|while|do|switch|case|break|continue|default|goto|try|catch|throw|new|delete|this|sizeof|typeid|decltype|noexcept)\b", "keyword"),
            (r"\b(\d+\.?\d*[fFuUlLxX]*|0x[0-9a-fA-F]+|0b[01]+)\b", "number"),
            (r"\b([A-Z_][A-Z0-9_]*)\b", "constant"),
            (r"\b(\w+_t)\b", "type"),
            (r"\b(\w+)(?=\s*\()", "function"),
        ]

    def highlightBlock(self, text):
        self.setFormat(0, len(text), QTextCharFormat())
        
        formatted = [False] * len(text)
        
        comment_patterns = [
            (r"//[^\n]*", "comment"),
            (r"/\*[\s\S]*?\*/", "comment"),
        ]
        
        for pattern, fmt_name in comment_patterns:
            rx = QRegularExpression(pattern)
            match = rx.globalMatch(text)
            while match.hasNext():
                m = match.next()
                start = m.capturedStart()
                end = start + m.capturedLength()
                for i in range(start, min(end, len(formatted))):
                    formatted[i] = True
                self.setFormat(start, m.capturedLength(), self._formats[fmt_name])
        
        for pattern, fmt_name in self._patterns:
            if fmt_name == "comment":
                continue
            rx = QRegularExpression(pattern)
            match = rx.globalMatch(text)
            while match.hasNext():
                m = match.next()
                start = m.capturedStart()
                end = start + m.capturedLength()
                skip = False
                for i in range(start, min(end, len(formatted))):
                    if formatted[i]:
                        skip = True
                        break
                if not skip:
                    self.setFormat(start, m.capturedLength(), self._formats[fmt_name])


class CSharpHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self._formats = {}

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))
        keyword_format.setFontWeight(700)
        self._formats["keyword"] = keyword_format

        type_format = QTextCharFormat()
        type_format.setForeground(QColor(78, 201, 176))
        self._formats["type"] = type_format

        class_format = QTextCharFormat()
        class_format.setForeground(QColor(78, 201, 176))
        class_format.setFontWeight(700)
        self._formats["class"] = class_format

        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))
        self._formats["string"] = string_format

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))
        self._formats["comment"] = comment_format

        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor(155, 155, 155))
        self._formats["preprocessor"] = preprocessor_format

        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))
        self._formats["number"] = number_format

        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))
        self._formats["function"] = function_format

        constant_format = QTextCharFormat()
        constant_format.setForeground(QColor(86, 156, 214))
        self._formats["constant"] = constant_format

        self._patterns = [
            (r"//[^\n]*", "comment"),
            (r"/\*[\s\S]*?\*/", "comment"),
            (r'"[^"\\]*(\\.[^"\\]*)*"', "string"),
            (r'@"[^"]*"', "string"),
            (r"\b(true|false|null)\b", "constant"),
            (r"\b(abstract|as|base|bool|break|byte|case|catch|char|checked|class|const|continue|decimal|default|delegate|do|double|else|enum|event|explicit|extern|false|finally|fixed|float|for|foreach|goto|if|implicit|in|int|interface|internal|is|lock|long|namespace|new|null|object|operator|out|override|params|private|protected|public|readonly|ref|return|sbyte|sealed|short|sizeof|stackalloc|static|string|struct|switch|this|throw|true|try|typeof|uint|ulong|unchecked|unsafe|ushort|using|virtual|void|volatile|while)\b", "keyword"),
            (r"\b(var|dynamic|async|await|get|set|value|where|select|from|join|orderby|group|by|into|let|on|equals|ascending|descending)\b", "keyword"),
            (r"\b(\d+\.?\d*[fFdDmM]?)\b", "number"),
            (r"\b([A-Z_][A-Z0-9_]*)\b", "constant"),
            (r"\b(\w+)(?=\s*\()", "function"),
        ]

    def highlightBlock(self, text):
        self.setFormat(0, len(text), QTextCharFormat())
        
        formatted = [False] * len(text)
        
        comment_patterns = [
            (r"//[^\n]*", "comment"),
            (r"/\*[\s\S]*?\*/", "comment"),
        ]
        
        for pattern, fmt_name in comment_patterns:
            rx = QRegularExpression(pattern)
            match = rx.globalMatch(text)
            while match.hasNext():
                m = match.next()
                start = m.capturedStart()
                end = start + m.capturedLength()
                for i in range(start, min(end, len(formatted))):
                    formatted[i] = True
                self.setFormat(start, m.capturedLength(), self._formats[fmt_name])
        
        for pattern, fmt_name in self._patterns:
            if fmt_name == "comment":
                continue
            rx = QRegularExpression(pattern)
            match = rx.globalMatch(text)
            while match.hasNext():
                m = match.next()
                start = m.capturedStart()
                end = start + m.capturedLength()
                skip = False
                for i in range(start, min(end, len(formatted))):
                    if formatted[i]:
                        skip = True
                        break
                if not skip:
                    self.setFormat(start, m.capturedLength(), self._formats[fmt_name])


class CodeViewDialog(QDialog):
    MAX_HISTORY = 10

    def __init__(self, header: str, cpp: str, class_name: str, parent=None, language: str = "cpp", 
                 project=None, code_gen=None, project_path: str = ""):
        super().__init__(parent)
        set_transparent_titlebar(self)
        self._header = header
        self._cpp = cpp
        self._class_name = class_name
        self._language = language
        self._project = project
        self._code_gen = code_gen
        self._project_path = project_path
        self._settings = QSettings("SexyUIEditor", "SexyUIEditor")
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle(tr("code.title", "Generated Code"))
        self.resize(900, 700)

        layout = QVBoxLayout(self)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs)

        if self._language == "csharp":
            self._cs_edit = QTextEdit()
            self._cs_edit.setReadOnly(True)
            self._cs_edit.setPlainText(self._cpp)
            self._cs_edit.setFont(QFont("Consolas", 10))
            self._cs_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: none;
                }
            """)
            self._cs_highlighter = CSharpHighlighter(self._cs_edit.document())
            self._tabs.addTab(self._cs_edit, f"{self._class_name}.cs")
        else:
            self._header_edit = QTextEdit()
            self._header_edit.setReadOnly(True)
            self._header_edit.setPlainText(self._header)
            self._header_edit.setFont(QFont("Consolas", 10))
            self._header_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: none;
                }
            """)
            self._header_highlighter = CppHighlighter(self._header_edit.document())
            self._tabs.addTab(self._header_edit, f"{self._class_name}.h")

            self._cpp_edit = QTextEdit()
            self._cpp_edit.setReadOnly(True)
            self._cpp_edit.setPlainText(self._cpp)
            self._cpp_edit.setFont(QFont("Consolas", 10))
            self._cpp_edit.setStyleSheet("""
                QTextEdit {
                    background-color: #1e1e1e;
                    color: #d4d4d4;
                    border: none;
                }
            """)
            self._cpp_highlighter = CppHighlighter(self._cpp_edit.document())
            self._tabs.addTab(self._cpp_edit, f"{self._class_name}.cpp")

        export_layout = QHBoxLayout()
        export_layout.addWidget(QLabel(tr("code.export_dir", "Export Directory:")))
        self._export_dir = QComboBox()
        self._export_dir.setEditable(True)
        self._load_history()
        if self._project_path:
            default_dir = os.path.dirname(self._project_path)
            self._export_dir.setCurrentText(default_dir)
        else:
            self._export_dir.setCurrentText("")
        export_layout.addWidget(self._export_dir, 1)
        layout.addLayout(export_layout)

        btn_layout = QHBoxLayout()
        
        if self._project and self._code_gen and len(self._project.interfaces) > 1:
            self._export_all_btn = QPushButton(tr("code.export_all", "Export All Interfaces"))
            btn_layout.addWidget(self._export_all_btn)
            self._export_all_btn.clicked.connect(self._export_all)
        
        btn_layout.addStretch()
        self._export_btn = QPushButton(tr("code.export", "Export Files"))
        self._browse_btn = QPushButton(tr("code.browse", "Browse..."))
        self._close_btn = QPushButton(tr("btn.close", "Close"))
        btn_layout.addWidget(self._browse_btn)
        btn_layout.addWidget(self._export_btn)
        btn_layout.addWidget(self._close_btn)
        layout.addLayout(btn_layout)

        self._browse_btn.clicked.connect(self._browse)
        self._export_btn.clicked.connect(self._export)
        self._close_btn.clicked.connect(self.reject)

    def _load_history(self):
        history = self._settings.value("export_history", [], type=list)
        self._export_dir.clear()
        self._export_dir.addItems(history)

    def _save_history(self, path: str):
        history = self._settings.value("export_history", [], type=list)
        if path in history:
            history.remove(path)
        history.insert(0, path)
        history = history[:self.MAX_HISTORY]
        self._settings.setValue("export_history", history)

    def _browse(self):
        folder = QFileDialog.getExistingDirectory(self, tr("code.export_dir", "Select Export Directory"))
        if folder:
            self._export_dir.setCurrentText(folder)

    def _get_export_dir(self) -> str:
        folder = self._export_dir.currentText().strip()
        if not folder:
            folder = QFileDialog.getExistingDirectory(self, tr("code.export_dir", "Select Export Directory"))
            if not folder:
                return ""
            self._export_dir.setCurrentText(folder)
        return folder

    def _export(self):
        folder = self._get_export_dir()
        if not folder:
            return

        if not os.path.isdir(folder):
            QMessageBox.warning(self, tr("error.title", "Error"), tr("code.dir_not_exist", "Directory does not exist"))
            return

        self._save_history(folder)
        
        if self._project:
            sync_result = self._sync_from_existing_files(folder)
            self._show_sync_result(sync_result)
            self._regenerate_code()
            self._save_project()

        if self._language == "csharp":
            cs_path = os.path.join(folder, f"{self._class_name}.cs")
            with open(cs_path, "w", encoding="utf-8") as f:
                f.write(self._cpp)
            QMessageBox.information(
                self, tr("code.exported", "Exported"),
                tr("code.export_success", "Files exported successfully") + f"\n{cs_path}"
            )
        else:
            header_path = os.path.join(folder, f"{self._class_name}.h")
            cpp_path = os.path.join(folder, f"{self._class_name}.cpp")

            with open(header_path, "w", encoding="utf-8") as f:
                f.write(self._header)
            with open(cpp_path, "w", encoding="utf-8") as f:
                f.write(self._cpp)

            QMessageBox.information(
                self, tr("code.exported", "Exported"),
                tr("code.export_success", "Files exported successfully") + f"\n{header_path}\n{cpp_path}"
            )

    def _show_sync_result(self, result: dict):
        if result["synced"] > 0:
            details = "\n".join(result["details"])
            QMessageBox.information(
                self,
                tr("code.sync_title", "Auto Sync"),
                tr("code.sync_success", "Synced user code from {} file(s):\n{}").format(result["synced"], details)
            )

    def _regenerate_code(self):
        if self._code_gen and self._project:
            iface = self._project.current_interface
            if iface:
                if self._language == "csharp":
                    self._cpp = self._code_gen.generate_csharp_for_interface(iface, self._project)
                else:
                    self._header = self._code_gen.generate_header_for_interface(iface, self._project)
                    self._cpp = self._code_gen.generate_cpp_for_interface(iface, self._project)

    def _save_project(self):
        if self._project and self._project_path:
            try:
                self._project.save(self._project_path)
            except Exception:
                pass

    def _sync_from_existing_files(self, folder: str) -> dict:
        result = {
            "synced": 0,
            "skipped": 0,
            "details": []
        }
        
        if not self._project:
            return result
        
        from core.code_parser import CodeParser
        
        for iface_id, iface in self._project.interfaces.items():
            class_name = iface.settings.class_name
            
            if self._language == "csharp":
                cs_file = os.path.join(folder, f"{class_name}.cs")
                if os.path.exists(cs_file):
                    try:
                        user_code = CodeParser.extract_from_cs_file(cs_file)
                        has_content = any([
                            user_code.declarations,
                            user_code.init_code,
                            user_code.destroy_code,
                            user_code.draw_code,
                            user_code.update_code,
                            user_code.functions,
                            user_code.event_handlers
                        ])
                        if has_content:
                            iface.user_code = user_code
                            result["synced"] += 1
                            result["details"].append(f"{class_name}.cs")
                        else:
                            result["skipped"] += 1
                    except Exception as e:
                        result["skipped"] += 1
                else:
                    result["skipped"] += 1
            else:
                header_file = os.path.join(folder, f"{class_name}.h")
                cpp_file = os.path.join(folder, f"{class_name}.cpp")
                
                if os.path.exists(header_file) and os.path.exists(cpp_file):
                    try:
                        user_code = CodeParser.extract_from_files(header_file, cpp_file)
                        has_content = any([
                            user_code.declarations,
                            user_code.init_code,
                            user_code.destroy_code,
                            user_code.draw_code,
                            user_code.update_code,
                            user_code.functions,
                            user_code.event_handlers
                        ])
                        if has_content:
                            iface.user_code = user_code
                            result["synced"] += 1
                            result["details"].append(f"{class_name}.h/.cpp")
                        else:
                            result["skipped"] += 1
                    except Exception as e:
                        result["skipped"] += 1
                else:
                    result["skipped"] += 1
        
        return result

    def _export_all(self):
        if not self._project or not self._code_gen:
            return

        if not self._project.interfaces:
            QMessageBox.information(self, tr("info.title", "Info"), tr("info.no_interfaces", "No interfaces to export."))
            return

        folder = self._get_export_dir()
        if not folder:
            return

        if not os.path.isdir(folder):
            QMessageBox.warning(self, tr("error.title", "Error"), tr("code.dir_not_exist", "Directory does not exist"))
            return

        self._save_history(folder)
        
        sync_result = self._sync_from_existing_files(folder)
        self._show_sync_result(sync_result)
        self._save_project()

        all_code = self._code_gen.generate_all_interfaces(self._project, self._language)
        exported_count = 0
        exported_files = []

        if self._language == "csharp":
            for class_name, (cs_code, _) in all_code.items():
                cs_path = os.path.join(folder, f"{class_name}.cs")
                with open(cs_path, 'w', encoding='utf-8') as f:
                    f.write(cs_code)
                exported_files.append(cs_path)
                exported_count += 1
        else:
            for class_name, (header, cpp) in all_code.items():
                header_path = os.path.join(folder, f"{class_name}.h")
                cpp_path = os.path.join(folder, f"{class_name}.cpp")

                with open(header_path, 'w', encoding='utf-8') as f:
                    f.write(header)
                with open(cpp_path, 'w', encoding='utf-8') as f:
                    f.write(cpp)

                exported_files.append(header_path)
                exported_files.append(cpp_path)
                exported_count += 1

        QMessageBox.information(
            self,
            tr("code.export_success", "Export Successful"),
            tr("status.exported_all", "Exported {} interfaces to:\n{}").format(exported_count, folder)
        )
