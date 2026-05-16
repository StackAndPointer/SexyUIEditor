# -*- coding: utf-8 -*-
import copy
from typing import List, Callable, Optional


class UndoCommand:
    def __init__(self, description: str = "",
                 redo_func: Optional[Callable] = None,
                 undo_func: Optional[Callable] = None):
        self.description = description
        self._redo_func = redo_func
        self._undo_func = undo_func

    def redo(self):
        if self._redo_func:
            self._redo_func()

    def undo(self):
        if self._undo_func:
            self._undo_func()


class UndoManager:
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self._undo_stack: List[UndoCommand] = []
        self._redo_stack: List[UndoCommand] = []
        self._max_size = 100
        self._on_changed: Optional[Callable] = None

    def set_on_changed(self, callback: Callable):
        self._on_changed = callback

    def push(self, command: UndoCommand):
        self._undo_stack.append(command)
        self._redo_stack.clear()
        if len(self._undo_stack) > self._max_size:
            self._undo_stack.pop(0)
        if self._on_changed:
            self._on_changed()

    def push_action(self, description: str, redo_func: Callable, undo_func: Callable):
        self.push(UndoCommand(description, redo_func, undo_func))

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        if self._on_changed:
            self._on_changed()
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        cmd = self._redo_stack.pop()
        cmd.redo()
        self._undo_stack.append(cmd)
        if self._on_changed:
            self._on_changed()
        return True

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo_description(self) -> str:
        return self._undo_stack[-1].description if self._undo_stack else ""

    def redo_description(self) -> str:
        return self._redo_stack[-1].description if self._redo_stack else ""

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()
        if self._on_changed:
            self._on_changed()


def snapshot_undo(project, description: str):
    from core.project import Project
    before = copy.deepcopy(project.to_dict())

    def undo():
        project.from_dict(copy.deepcopy(before))

    return undo


def snapshot_redo(project, description: str):
    from core.project import Project
    after = copy.deepcopy(project.to_dict())

    def redo():
        project.from_dict(copy.deepcopy(after))

    return redo
