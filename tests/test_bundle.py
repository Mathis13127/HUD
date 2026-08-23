"""Unit tests for the single-file HUD Widget Bundle system."""

from pathlib import Path

import pytest

from hud.api.models import HudWidgetManifest, WidgetPlacement
from hud.bundle.loader import HudBundleLoader
from hud.bundle.manifest import parse_manifest
from hud.errors import ManifestValidationError, WidgetLoadError


def test_parse_manifest_valid() -> None:
    data = {
        "id": "test.hud.widget",
        "name": "Test Widget",
        "version": "1.0",
        "author": "Mathis",
        "entry_point": "MyWidget"
    }
    manifest = parse_manifest(data)
    
    assert isinstance(manifest, HudWidgetManifest)
    assert manifest.id == "test.hud.widget"
    assert manifest.name == "Test Widget"
    assert manifest.version == "1.0"
    assert manifest.entry_point == "MyWidget"


def test_parse_manifest_missing_required() -> None:
    data = {
        # missing id and name
        "version": "1.0"
    }
    with pytest.raises(ManifestValidationError) as exc:
        parse_manifest(data)
    assert "id" in exc.value.missing_fields
    assert "name" in exc.value.missing_fields


def test_bundle_loader_dynamic_import(tmp_path: Path) -> None:
    widget_file = tmp_path / "my_widget.py"
    widget_file.write_text(
        "MANIFEST = {\n"
        "    'id': 'jarvis.hud.test',\n"
        "    'name': 'Test'\n"
        "}\n"
        "class Widget:\n"
        "    pass\n",
        encoding="utf-8"
    )

    loader = HudBundleLoader()
    instance, manifest = loader.load_bundle(widget_file)

    assert manifest.id == "jarvis.hud.test"
    assert manifest.name == "Test"
    assert type(instance).__name__ == "Widget"


def test_bundle_loader_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "does_not_exist.py"
    loader = HudBundleLoader()

    with pytest.raises(WidgetLoadError) as exc:
        loader.load_bundle(missing_file)
    assert "unknown" == exc.value.bundle_id


def test_bundle_loader_missing_manifest(tmp_path: Path) -> None:
    widget_file = tmp_path / "bad.py"
    widget_file.write_text(
        "class Widget:\n"
        "    pass\n",
        encoding="utf-8"
    )

    loader = HudBundleLoader()

    with pytest.raises(WidgetLoadError) as exc:
        loader.load_bundle(widget_file)
    assert "Bundle is missing 'MANIFEST' dictionary" in str(exc.value)
