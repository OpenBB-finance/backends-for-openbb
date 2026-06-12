#!/usr/bin/env python3
"""
Validate apps.json for OpenBB Workspace compatibility.

Usage:
    python scripts/validate_apps.py <app_path>
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


class AppsValidator:
    def __init__(self, app_path: Path):
        self.app_path = app_path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.widget_ids: set[str] = set()
        self.layouts_validated = 0

    def validate(self) -> bool:
        apps_path = self.app_path / "apps.json"
        widgets_path = self.app_path / "widgets.json"

        if not apps_path.exists():
            self.warnings.append("apps.json not found (optional file)")
            return True

        self._load_widget_ids(widgets_path)

        try:
            with open(apps_path, "r", encoding="utf-8") as file:
                apps = json.load(file)
        except json.JSONDecodeError as exc:
            self.errors.append(f"Invalid JSON in apps.json: {exc}")
            return False

        if not isinstance(apps, list):
            self.errors.append("apps.json must be an ARRAY of app objects")
            return False

        if not apps:
            self.warnings.append("apps.json is an empty array")
            return True

        for index, app in enumerate(apps):
            if not isinstance(app, dict):
                self.errors.append(f"[app[{index}]] App entry must be an object")
                continue
            self._validate_app(f"app[{index}]", app)

        return not self.errors

    def _load_widget_ids(self, widgets_path: Path) -> None:
        if not widgets_path.exists():
            return
        try:
            with open(widgets_path, "r", encoding="utf-8") as file:
                widgets = json.load(file)
        except json.JSONDecodeError:
            self.warnings.append("Cannot parse widgets.json for reference check")
            return

        if isinstance(widgets, dict):
            self.widget_ids = set(widgets.keys())
        elif isinstance(widgets, list):
            self.warnings.append(
                "widgets.json is an array; widget cross-reference checks may be incomplete"
            )

    def _validate_app(self, prefix: str, app: dict[str, Any]) -> None:
        if "name" not in app:
            self.errors.append(f"[{prefix}] Missing required field: name")

        if "allowCustomization" not in app:
            self.errors.append(f"[{prefix}] Missing required field: allowCustomization")
        elif not isinstance(app["allowCustomization"], bool):
            self.errors.append(f"[{prefix}] allowCustomization must be a boolean")

        if "tabs" not in app:
            self.errors.append(f"[{prefix}] Missing required field: tabs")
        elif not isinstance(app["tabs"], dict):
            self.errors.append(f"[{prefix}] tabs must be an object")
        elif not app["tabs"]:
            self.errors.append(f"[{prefix}] tabs must not be empty")
        else:
            for tab_id, tab in app["tabs"].items():
                self._validate_tab(f"{prefix}.tabs.{tab_id}", tab)

        if "groups" not in app:
            self.warnings.append(f"[{prefix}] Missing groups; safest default is []")
        elif not isinstance(app["groups"], list):
            self.errors.append(f"[{prefix}] groups must be an array")
        else:
            for index, group in enumerate(app["groups"]):
                self._validate_group(f"{prefix}.groups[{index}]", group)

        if "description" not in app:
            self.warnings.append(f"[{prefix}] Missing description")

        for key in ("img", "img_dark", "img_light"):
            if key in app and not isinstance(app[key], str):
                self.errors.append(f"[{prefix}] {key} must be a string")

        prompts = app.get("prompts")
        if prompts is None:
            self.warnings.append(f"[{prefix}] Missing prompts; safest default is []")
        elif not isinstance(prompts, list):
            self.errors.append(f"[{prefix}] prompts must be an array")
        else:
            for index, prompt in enumerate(prompts):
                if not isinstance(prompt, str):
                    self.errors.append(f"[{prefix}] prompts[{index}] must be a string")

    def _validate_tab(self, prefix: str, tab: Any) -> None:
        if not isinstance(tab, dict):
            self.errors.append(f"[{prefix}] tab must be an object")
            return

        if "id" not in tab:
            self.warnings.append(f"[{prefix}] Missing tab id")
        if "name" not in tab:
            self.warnings.append(f"[{prefix}] Missing tab name")

        layout = tab.get("layout")
        if not isinstance(layout, list):
            self.errors.append(f"[{prefix}] layout must be an array")
            return
        if not layout:
            self.warnings.append(f"[{prefix}] Empty layout")
            return

        positions: list[tuple[str, int, int, int, int]] = []
        for index, item in enumerate(layout):
            self._validate_layout_item(f"{prefix}.layout[{index}]", item, positions)
        self.layouts_validated += 1

    def _validate_layout_item(
        self,
        prefix: str,
        item: Any,
        positions: list[tuple[str, int, int, int, int]],
    ) -> None:
        if not isinstance(item, dict):
            self.errors.append(f"[{prefix}] layout item must be an object")
            return

        widget_id = item.get("i")
        if not widget_id:
            self.errors.append(f"[{prefix}] Missing widget ID (i)")
            return

        if self.widget_ids and widget_id not in self.widget_ids:
            self.errors.append(f"[{prefix}] Widget '{widget_id}' not found in widgets.json")

        coords: dict[str, Any] = {
            "x": item.get("x", 0),
            "y": item.get("y", 0),
            "w": item.get("w", 12),
            "h": item.get("h", 8),
        }
        for name, value in coords.items():
            if not isinstance(value, (int, float)):
                self.errors.append(f"[{prefix}] {name} must be a number")
                return

        x, y, w, h = int(coords["x"]), int(coords["y"]), int(coords["w"]), int(coords["h"])
        if x < 0 or y < 0:
            self.errors.append(f"[{prefix}] x and y cannot be negative")
        if w <= 0 or h <= 0:
            self.errors.append(f"[{prefix}] w and h must be positive")
        if x + w > 40:
            self.errors.append(f"[{prefix}] Widget extends beyond the 40-column grid")

        for other_id, ox, oy, ow, oh in positions:
            if not (x + w <= ox or ox + ow <= x or y + h <= oy or oy + oh <= y):
                self.warnings.append(
                    f"[{prefix}] Widget '{widget_id}' may overlap with '{other_id}'"
                )
                break
        positions.append((widget_id, x, y, w, h))

        groups = item.get("groups")
        if groups is not None:
            if not isinstance(groups, list):
                self.errors.append(f"[{prefix}] groups must be an array")
            elif not all(isinstance(group, str) for group in groups):
                self.errors.append(f"[{prefix}] group names must be strings")

        state = item.get("state")
        if state is not None and not isinstance(state, dict):
            self.errors.append(f"[{prefix}] state must be an object")

    def _validate_group(self, prefix: str, group: Any) -> None:
        if not isinstance(group, dict):
            self.errors.append(f"[{prefix}] group must be an object")
            return

        name = group.get("name")
        if not isinstance(name, str):
            self.errors.append(f"[{prefix}] Missing group name")
        elif not re.match(r"^Group \d+$", name):
            self.warnings.append(
                f"[{prefix}] Group name '{name}' does not follow the recommended 'Group N' pattern"
            )

        group_type = group.get("type")
        if group_type not in (None, "param", "endpointParam"):
            self.warnings.append(f"[{prefix}] Unknown group type '{group_type}'")

        if "paramName" not in group:
            self.warnings.append(f"[{prefix}] Missing paramName")

        widget_ids = group.get("widgetIds")
        if widget_ids is None:
            self.errors.append(f"[{prefix}] Missing widgetIds")
            return
        if not isinstance(widget_ids, list):
            self.errors.append(f"[{prefix}] widgetIds must be an array")
            return
        if not widget_ids:
            self.errors.append(f"[{prefix}] widgetIds must contain at least one widget")
            return

        for widget_id in widget_ids:
            if not isinstance(widget_id, str):
                self.errors.append(f"[{prefix}] widgetIds must contain strings")
            elif self.widget_ids and widget_id not in self.widget_ids:
                self.errors.append(
                    f"[{prefix}] Group references unknown widget '{widget_id}'"
                )

    def report(self) -> None:
        print("\n" + "=" * 60)
        print("APPS VALIDATION REPORT")
        print("=" * 60)
        print(f"Path: {self.app_path}")
        print(f"Widget IDs loaded: {len(self.widget_ids)}")
        print(f"Tab layouts validated: {self.layouts_validated}")

        if self.errors:
            print(f"\n[ERRORS] ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print(f"\n[WARNINGS] ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")

        if not self.errors and not self.warnings:
            print("\n[OK] All validations passed!")
        elif not self.errors:
            print("\n[OK] Validation passed with warnings")

        print("\n" + "=" * 60)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python validate_apps.py <app_path>")
        sys.exit(1)

    app_path = Path(sys.argv[1])
    if not app_path.exists():
        print(f"Error: Path does not exist: {app_path}")
        sys.exit(1)
    if not app_path.is_dir():
        app_path = app_path.parent

    validator = AppsValidator(app_path)
    is_valid = validator.validate()
    validator.report()
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
