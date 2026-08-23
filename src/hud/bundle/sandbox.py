"""AST-based Sandbox for validating dynamically injected HUD widgets."""

import ast

from hud.errors import HudError


class WidgetSecurityError(HudError):
    """Raised when injected code violates security policies."""
    def __init__(self, reason: str) -> None:
        super().__init__(
            code="hud.bundle.security_violation",
            message=f"Widget code rejected by sandbox: {reason}"
        )


class HudAstValidator(ast.NodeVisitor):
    """Parses Python source code and ensures it only contains allowed operations."""

    ALLOWED_MODULES = {"PySide6", "typing", "hud"}
    BANNED_BUILTINS = {"open", "eval", "exec", "globals", "locals", "__import__", "compile"}

    def validate(self, source_code: str) -> None:
        """Parse and validate the given source code.
        
        Raises:
            WidgetSecurityError: If the code is invalid or malicious.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise WidgetSecurityError(f"SyntaxError: {e}")
            
        self.visit(tree)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            root = alias.name.split(".")[0]
            if root not in self.ALLOWED_MODULES:
                raise WidgetSecurityError(f"Importing '{root}' is forbidden.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            root = node.module.split(".")[0]
            if root not in self.ALLOWED_MODULES:
                raise WidgetSecurityError(f"Importing from '{root}' is forbidden.")
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Name):
            if node.func.id in self.BANNED_BUILTINS:
                raise WidgetSecurityError(f"Calling built-in '{node.func.id}' is forbidden.")
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        # Prevent introspection escapes like obj.__class__.__subclasses__()
        # Defining __init__ in a class is safe (ast.FunctionDef), but accessing
        # dunder attributes dynamically is a red flag in UI code.
        if node.attr.startswith("__") and node.attr.endswith("__"):
            if node.attr not in ("__name__", "__class__", "__init__"):
                raise WidgetSecurityError(f"Access to magic attribute '{node.attr}' is forbidden.")
        self.generic_visit(node)
