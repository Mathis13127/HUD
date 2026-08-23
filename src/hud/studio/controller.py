"""Central controller orchestrating HUD Studio UI and Overlay Manager."""

from pathlib import Path

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QFileDialog

from hud.errors import HudError
from hud.overlay.manager import HudOverlayManager
from hud.studio.panels.editor import WorkspaceEditor
from hud.studio.panels.explorer import BundleExplorer
from hud.studio.panels.preview_control import ControlPanel


NEW_WIDGET_TEMPLATE = '''from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

from hud.api.models import WidgetPlacement

MANIFEST = {
    "id": "jarvis.hud.new_widget",
    "name": "Nouveau Widget",
    "version": "1.0",
    "default_placement": WidgetPlacement(anchor="center")
}

class Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Exemple de label
        lbl = QLabel("Hello World!")
        lbl.setStyleSheet("color: white; font-size: 24px; font-weight: bold; background: rgba(0, 0, 0, 180); padding: 15px; border-radius: 10px;")
        layout.addWidget(lbl)
        
        # Pour charger une image qui se trouverait à côté de ce fichier :
        # from PySide6.QtGui import QPixmap
        # img_path = Path(__file__).parent / "logo.png"
        # pixmap = QPixmap(str(img_path))
        
    def mount(self):
        """Appelé juste après que le widget ait été ajouté à l'overlay."""
        pass
'''


class StudioController(QObject):
    """Bridges the Editor UI with the HUD Overlay Manager to provide Live-Coding."""

    def __init__(
        self,
        overlay_manager: HudOverlayManager,
        explorer: BundleExplorer,
        editor: WorkspaceEditor,
        control: ControlPanel,
        bundles_dir: Path,
    ) -> None:
        super().__init__()
        self._manager = overlay_manager
        self._explorer = explorer
        self._editor = editor
        self._control = control
        self._bundles_dir = bundles_dir
        
        self._active_file_path: Path | None = None
        self._active_bundle_id: str | None = None

        self._connect_signals()

    def _connect_signals(self) -> None:
        # When a file is clicked in the tree
        self._explorer.tree.clicked.connect(self._on_file_selected)
        # When deploy is clicked
        self._control.btn_deploy.clicked.connect(self.deploy_active_bundle)
        # When new widget is clicked
        self._explorer.btn_new_widget.clicked.connect(self.create_new_widget)

    def create_new_widget(self) -> None:
        """Prompt user for a filename, create a boilerplate widget, and open it."""
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Créer un nouveau widget HUD",
            str(self._bundles_dir),
            "Python Files (*.py)"
        )
        if not file_path:
            return
            
        path = Path(file_path)
        if not path.suffix == ".py":
            path = path.with_suffix(".py")
            
        try:
            path.write_text(NEW_WIDGET_TEMPLATE, encoding="utf-8")
            self._control.log_message(f"Nouveau widget créé: {path.name}")
            
            # Auto-open in editor
            self._active_file_path = path
            self._editor.load_file_content(str(path), NEW_WIDGET_TEMPLATE)
        except Exception as e:
            self._control.log_message(f"Erreur lors de la création: {e}", is_error=True)

    def _on_file_selected(self, index) -> None:
        """Handle user selecting a file from the explorer."""
        file_path = Path(self._explorer.model.filePath(index))
        if file_path.is_file() and file_path.suffix == ".py":
            self._active_file_path = file_path
            try:
                content = file_path.read_text(encoding="utf-8")
                self._editor.load_file_content(str(file_path), content)
                self._control.log_message(f"Opened {file_path.name}")
            except Exception as e:
                self._control.log_message(f"Failed to open {file_path.name}: {e}", is_error=True)

    def deploy_active_bundle(self) -> None:
        """Save the active file, perform a dry run, and hot-reload the overlay."""
        if not self._active_file_path:
            self._control.log_message("Aucun fichier actif sélectionné.", is_error=True)
            return

        # 1. Save File
        try:
            self._active_file_path.write_text(self._editor.get_current_code(), encoding="utf-8")
            self._control.log_message(f"Fichier sauvegardé: '{self._active_file_path.name}'.")
        except Exception as e:
            self._control.log_message(f"Erreur de sauvegarde: {e}", is_error=True)
            return

        # 2. Dry Run & Mount
        self._control.log_message("Vérification et Rechargement...")
        
        if self._active_bundle_id:
            self._manager.unmount(self._active_bundle_id)

        try:
            new_id = self._manager.register(self._active_file_path)
            self._manager.mount(new_id)
            self._active_bundle_id = new_id
            self._control.log_message(f"✅ Hot-Reload Réussi: {new_id}")
        except HudError as e:
            self._control.log_message(f"❌ Erreur de Validation: {e.message}", is_error=True)
        except Exception as e:
            self._control.log_message(f"❌ Crash inattendu: {e}", is_error=True)
