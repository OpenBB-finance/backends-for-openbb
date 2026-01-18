#!/usr/bin/env python3
"""
Validate apps.json for OpenBB Workspace compatibility.

Usage:
    python scripts/validate_apps.py <app_path>
    python scripts/validate_apps.py apps/my-app/

Returns exit code 0 on success, 1 on validation errors.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class AppsValidator:
    """Validates apps.json files for OpenBB Workspace compatibility."""

    def __init__(self, app_path: Path):
        self.app_path = app_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.widget_ids: Set[str] = set()
        self.layouts_validated = 0

    def validate(self) -> bool:
        """
        Run all validations.

        Returns:
            True if validation passed (no errors), False otherwise.
        """
        apps_path = self.app_path / "apps.json"
        widgets_path = self.app_path / "widgets.json"

        if not apps_path.exists():
            self.warnings.append("apps.json not found (optional file)")
            return True  # apps.json is optional

        # Load widgets.json for reference validation
        if widgets_path.exists():
            try:
                with open(widgets_path, "r", encoding="utf-8") as f:
                    widgets = json.load(f)
                    if isinstance(widgets, list):
                        self.widget_ids = {
                            w.get("widgetId", w.get("endpoint", ""))
                            for w in widgets
                        }
                    elif isinstance(widgets, dict):
                        self.widget_ids = set(widgets.keys())
            except json.JSONDecodeError:
                self.warnings.append(
                    "Cannot parse widgets.json for reference check"
                )

        # Load apps.json
        try:
            with open(apps_path, "r", encoding="utf-8") as f:
                apps = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in apps.json: {e}")
            return False

        # apps.json MUST be an array of app objects
        # OpenBB Workspace expects array format
        if isinstance(apps, list):
            if len(apps) == 0:
                self.warnings.append("apps.json is an empty array")
            for i, app in enumerate(apps):
                self._validate_app(f"app[{i}]", app)
        elif isinstance(apps, dict):
            self.errors.append(
                "apps.json must be an ARRAY of app objects, not a single object.\n"
                "   Expected: [{\"name\": \"App Name\", \"tabs\": {...}}]\n"
                "   Received: {\"name\": \"App Name\", ...}"
            )
            return False
        else:
            self.errors.append(
                f"apps.json must be an array, got {type(apps).__name__}"
            )
            return False

        return len(self.errors) == 0

    def _validate_app(self, prefix: str, app: Dict[str, Any]) -> None:
        """Validate a single app configuration."""
        # Required fields
        if "name" not in app:
            self.errors.append(f"[{prefix}] Missing required field: name")

        # Optional but recommended fields
        if "description" not in app:
            self.warnings.append(f"[{prefix}] Missing description")

        # Image validation
        for img_key in ["img", "img_dark", "img_light"]:
            if img_key in app:
                img_url = app[img_key]
                if not isinstance(img_url, str):
                    self.errors.append(f"[{prefix}] {img_key} must be a string URL")
                elif not img_url.startswith(("http://", "https://", "/")):
                    self.warnings.append(
                        f"[{prefix}] {img_key} should be an absolute URL"
                    )

        # Tabs validation
        tabs = app.get("tabs", {})
        if not tabs:
            self.warnings.append(f"[{prefix}] No tabs defined")
        elif not isinstance(tabs, dict):
            self.errors.append(f"[{prefix}] tabs must be an object")
        else:
            for tab_id, tab in tabs.items():
                self._validate_tab(f"{prefix}.tabs.{tab_id}", tab)

        # Groups validation
        groups = app.get("groups", [])
        if groups:
            if not isinstance(groups, list):
                self.errors.append(f"[{prefix}] groups must be an array")
            else:
                for i, group in enumerate(groups):
                    self._validate_group(f"{prefix}.groups[{i}]", group)

        # Prompts validation (optional AI prompts)
        prompts = app.get("prompts", [])
        if prompts:
            if not isinstance(prompts, list):
                self.errors.append(f"[{prefix}] prompts must be an array")
            else:
                for i, prompt in enumerate(prompts):
                    if not isinstance(prompt, str):
                        self.errors.append(
                            f"[{prefix}] prompts[{i}] must be a string"
                        )

    def _validate_tab(self, prefix: str, tab: Dict[str, Any]) -> None:
        """Validate a single tab configuration."""
        if not isinstance(tab, dict):
            self.errors.append(f"[{prefix}] tab must be an object")
            return

        # Tab name
        if "name" not in tab:
            self.warnings.append(f"[{prefix}] Missing tab name")

        # Tab id (should match key)
        if "id" not in tab:
            self.warnings.append(f"[{prefix}] Missing tab id")

        # Layout validation
        layout = tab.get("layout", [])
        if not layout:
            self.warnings.append(f"[{prefix}] Empty layout")
            return

        if not isinstance(layout, list):
            self.errors.append(f"[{prefix}] layout must be an array")
            return

        # Track positions for overlap detection
        positions: List[Tuple[str, int, int, int, int]] = []

        for i, item in enumerate(layout):
            self._validate_layout_item(f"{prefix}.layout[{i}]", item, positions)

        self.layouts_validated += 1

    def _validate_layout_item(
        self,
        prefix: str,
        item: Dict[str, Any],
        positions: List[Tuple[str, int, int, int, int]]
    ) -> None:
        """Validate a single layout item."""
        if not isinstance(item, dict):
            self.errors.append(f"[{prefix}] layout item must be an object")
            return

        # Widget ID
        widget_id = item.get("i")
        if not widget_id:
            self.errors.append(f"[{prefix}] Missing widget ID (i)")
            return

        # Check widget exists in widgets.json
        if self.widget_ids and widget_id not in self.widget_ids:
            self.errors.append(
                f"[{prefix}] Widget '{widget_id}' not found in widgets.json"
            )

        # Position validation
        x = item.get("x", 0)
        y = item.get("y", 0)
        w = item.get("w", 12)
        h = item.get("h", 8)

        # Type checks
        for coord_name, coord_val in [("x", x), ("y", y), ("w", w), ("h", h)]:
            if not isinstance(coord_val, (int, float)):
                self.errors.append(
                    f"[{prefix}] {coord_name} must be a number"
                )

        # Range checks
        if x < 0:
            self.errors.append(f"[{prefix}] x cannot be negative (got {x})")
        if y < 0:
            self.errors.append(f"[{prefix}] y cannot be negative (got {y})")
        if w <= 0:
            self.errors.append(f"[{prefix}] w must be positive (got {w})")
        if h <= 0:
            self.errors.append(f"[{prefix}] h must be positive (got {h})")

        # Grid bounds check (40 columns max)
        if x + w > 40:
            self.errors.append(
                f"[{prefix}] Widget extends beyond grid "
                f"(x={x} + w={w} = {x+w} > 40)"
            )

        # Check for overlaps
        for other_id, ox, oy, ow, oh in positions:
            if self._rectangles_overlap(x, y, w, h, ox, oy, ow, oh):
                self.warnings.append(
                    f"[{prefix}] Widget '{widget_id}' may overlap with '{other_id}'"
                )
                break

        positions.append((widget_id, x, y, w, h))

        # State validation (optional pre-configuration)
        if "state" in item:
            self._validate_widget_state(prefix, item["state"])

        # Groups reference
        if "groups" in item:
            groups = item["groups"]
            if not isinstance(groups, list):
                self.errors.append(f"[{prefix}] groups must be an array")
            else:
                for g in groups:
                    if not isinstance(g, str):
                        self.errors.append(
                            f"[{prefix}] group name must be a string"
                        )

    def _rectangles_overlap(
        self,
        x1: int, y1: int, w1: int, h1: int,
        x2: int, y2: int, w2: int, h2: int
    ) -> bool:
        """Check if two rectangles overlap."""
        return not (
            x1 + w1 <= x2 or  # First is left of second
            x2 + w2 <= x1 or  # Second is left of first
            y1 + h1 <= y2 or  # First is above second
            y2 + h2 <= y1     # Second is above first
        )

    def _validate_widget_state(self, prefix: str, state: Dict[str, Any]) -> None:
        """Validate widget state configuration."""
        if not isinstance(state, dict):
            self.errors.append(f"[{prefix}] state must be an object")
            return

        # Validate params in state
        if "params" in state:
            params = state["params"]
            if not isinstance(params, dict):
                self.errors.append(f"[{prefix}] state.params must be an object")

        # Validate chartView
        if "chartView" in state:
            chart_view = state["chartView"]
            if not isinstance(chart_view, dict):
                self.errors.append(f"[{prefix}] state.chartView must be an object")

        # Validate columnState
        if "columnState" in state:
            col_state = state["columnState"]
            if not isinstance(col_state, dict):
                self.errors.append(
                    f"[{prefix}] state.columnState must be an object"
                )

    def _validate_group(self, prefix: str, group: Dict[str, Any]) -> None:
        """Validate a parameter group configuration."""
        if not isinstance(group, dict):
            self.errors.append(f"[{prefix}] group must be an object")
            return

        # Required fields
        if "name" not in group:
            self.errors.append(f"[{prefix}] Missing group name")

        # Type validation
        group_type = group.get("type")
        valid_types = ["param", "endpointParam"]
        if group_type and group_type not in valid_types:
            self.warnings.append(
                f"[{prefix}] Unknown group type: '{group_type}'. "
                f"Valid: {valid_types}"
            )

        # Param name
        if "paramName" not in group:
            self.warnings.append(f"[{prefix}] Missing paramName")

        # Widget IDs validation
        widget_ids = group.get("widgetIds", [])
        if not widget_ids:
            self.warnings.append(f"[{prefix}] No widgets in group")
        elif not isinstance(widget_ids, list):
            self.errors.append(f"[{prefix}] widgetIds must be an array")
        else:
            for wid in widget_ids:
                if self.widget_ids and wid not in self.widget_ids:
                    self.errors.append(
                        f"[{prefix}] Group references unknown widget: '{wid}'"
                    )

    def report(self) -> None:
        """Print validation report to stdout."""
        print("\n" + "=" * 60)
        print("APPS VALIDATION REPORT")
        print("=" * 60)
        print(f"Path: {self.app_path}")
        print(f"Widget IDs loaded: {len(self.widget_ids)}")
        print(f"Tab layouts validated: {self.layouts_validated}")

        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"   • {error}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   • {warning}")

        if not self.errors and not self.warnings:
            print("\n✅ All validations passed!")
        elif not self.errors:
            print("\n✅ Validation passed with warnings")

        print("\n" + "=" * 60)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_apps.py <app_path>")
        print("Example: python validate_apps.py apps/my-app/")
        sys.exit(1)

    app_path = Path(sys.argv[1])

    if not app_path.exists():
        print(f"Error: Path does not exist: {app_path}")
        sys.exit(1)

    if not app_path.is_dir():
        # If file passed, use parent directory
        app_path = app_path.parent

    validator = AppsValidator(app_path)
    is_valid = validator.validate()
    validator.report()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
