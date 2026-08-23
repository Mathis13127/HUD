"""Tests for the HUD Bundle Loader."""

import pytest

from hud.bundle.loader import HudBundleLoader
from hud.api.models import HudWidgetManifest
from hud.errors import WidgetLoadError, ManifestValidationError
from hud.bundle.manifest import parse_manifest


def test_parse_manifest_valid() -> None:
    raw_data = {
        "id": "jarvis.hud.orb",
        "name": "Orb Widget",
        "version": "1.0",
        "default_placement": {
            "anchor": "top_right",
            "offset_x": -20
        }
    }
    manifest = parse_manifest(raw_data)
    assert manifest.id == "jarvis.hud.orb"
    assert manifest.name == "Orb Widget"
    assert manifest.default_placement.anchor == "top_right"
    assert manifest.default_placement.offset_x == -20
    assert manifest.default_placement.offset_y == 0


def test_parse_manifest_missing_required() -> None:
    raw_data = {
        "name": "Orb Widget"
    }
    with pytest.raises(ManifestValidationError) as exc:
        parse_manifest(raw_data)
    assert "Missing" in str(exc.value)
    assert "id" in str(exc.value)


def test_bundle_loader_dynamic_import() -> None:
    code = (
        "MANIFEST = {\n"
        "    'id': 'jarvis.hud.test',\n"
        "    'name': 'Test'\n"
        "}\n"
        "class Widget:\n"
        "    pass\n"
    )

    loader = HudBundleLoader()
    instance, manifest = loader.load_bundle_from_source(code)

    assert manifest.id == "jarvis.hud.test"
    assert instance is not None
    assert type(instance).__name__ == "Widget"


def test_bundle_loader_missing_manifest() -> None:
    code = (
        "class Widget:\n"
        "    pass\n"
    )

    loader = HudBundleLoader()

    with pytest.raises(WidgetLoadError) as exc:
        loader.load_bundle_from_source(code)
    assert "Bundle is missing 'MANIFEST'" in str(exc.value) or "bundle is missing 'MANIFEST'" in str(exc.value)
