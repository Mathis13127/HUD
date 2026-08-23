"""Tests for the AST Sandbox Validator."""

import pytest

from hud.bundle.sandbox import HudAstValidator, WidgetSecurityError


def test_sandbox_allows_valid_pyside_code():
    code = """
from PySide6.QtWidgets import QWidget, QLabel
import typing

MANIFEST = {'id': 'test'}

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.label = QLabel("Hello")
        
    def mount(self):
        pass
"""
    validator = HudAstValidator()
    validator.validate(code)  # Should not raise


def test_sandbox_blocks_os_import():
    code = "import os\nos.system('dir')"
    validator = HudAstValidator()
    with pytest.raises(WidgetSecurityError) as exc:
        validator.validate(code)
    assert "Importing 'os' is forbidden" in str(exc.value)


def test_sandbox_blocks_banned_builtins():
    code = "x = open('test.txt', 'w')"
    validator = HudAstValidator()
    with pytest.raises(WidgetSecurityError) as exc:
        validator.validate(code)
    assert "Calling built-in 'open' is forbidden" in str(exc.value)


def test_sandbox_blocks_eval_exec():
    code = "exec('import os')"
    validator = HudAstValidator()
    with pytest.raises(WidgetSecurityError) as exc:
        validator.validate(code)
    assert "Calling built-in 'exec' is forbidden" in str(exc.value)


def test_sandbox_blocks_dunder_attributes_for_introspection():
    code = """
class Exploit:
    def hack(self):
        return self.__class__.__subclasses__()[0]()
"""
    validator = HudAstValidator()
    with pytest.raises(WidgetSecurityError) as exc:
        validator.validate(code)
    assert "Access to magic attribute '__subclasses__' is forbidden" in str(exc.value)
