#!/usr/bin/env python3
"""
Validate widgets.json for OpenBB Workspace compatibility.

Usage:
    python scripts/validate_widgets.py <app_path>
    python scripts/validate_widgets.py apps/my-app/

Returns exit code 0 on success, 1 on validation errors.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# Valid widget types
VALID_WIDGET_TYPES = [
    "table",
    "chart",
    "chart-highcharts",
    "markdown",
    "metric",
    "newsfeed",
    "html",
    "pdf",
    "multi_file_viewer",
    "advanced_charting",
    "live_grid",
    "omni",
    "ssrm_table",
]

# Valid parameter types
VALID_PARAM_TYPES = [
    "text",
    "number",
    "boolean",
    "date",
    "endpoint",
    "ticker",
    "tabs",
    "form",
]

# Valid cell data types for tables
VALID_CELL_DATA_TYPES = [
    "text",
    "number",
    "boolean",
    "date",
    "dateString",
    "object",
]

# Valid chart data types
VALID_CHART_DATA_TYPES = [
    "category",
    "series",
    "time",
    "excluded",
]

# Valid formatter functions
VALID_FORMATTER_FNS = [
    "int",
    "none",
    "percent",
    "normalized",
    "normalizedPercent",
    "dateToYear",
]

# Valid render functions
VALID_RENDER_FNS = [
    "greenRed",
    "titleCase",
    "hoverCard",
    "cellOnClick",
    "columnColor",
    "showCellChange",
]


class WidgetValidator:
    """Validates widgets.json files for OpenBB Workspace compatibility."""

    def __init__(self, app_path: Path):
        self.app_path = app_path
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.widget_ids: Set[str] = set()
        self.endpoint_names: Set[str] = set()

    def validate(self) -> bool:
        """
        Run all validations.

        Returns:
            True if validation passed (no errors), False otherwise.
        """
        widgets_path = self.app_path / "widgets.json"

        if not widgets_path.exists():
            self.errors.append(f"widgets.json not found at {widgets_path}")
            return False

        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                widgets = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

        # widgets.json MUST be an object/dict with widget IDs as keys
        # OpenBB Workspace rejects array format
        if isinstance(widgets, list):
            self.errors.append(
                "widgets.json must be an OBJECT with widget IDs as keys, not an array.\n"
                "   Expected: {\"widget_id\": {\"name\": \"Widget Name\", ...}}\n"
                "   Received: [{\"name\": \"Widget Name\", ...}]"
            )
            return False
        elif isinstance(widgets, dict):
            widgets_dict = widgets
        else:
            self.errors.append(
                f"widgets.json must be a dict, got {type(widgets).__name__}"
            )
            return False

        if not widgets_dict:
            self.warnings.append("widgets.json is empty")
            return True

        # Collect all widget IDs and endpoints first
        for widget_id, widget in widgets_dict.items():
            self.widget_ids.add(widget_id)
            if "endpoint" in widget:
                self.endpoint_names.add(widget["endpoint"])

        # Validate each widget
        for widget_id, widget in widgets_dict.items():
            self._validate_widget(widget_id, widget)

        return len(self.errors) == 0

    def _validate_widget(self, widget_id: str, widget: Dict[str, Any]) -> None:
        """Validate a single widget configuration."""
        prefix = f"[{widget_id}]"

        # Required fields
        required_fields = ["name", "type", "endpoint"]
        for field in required_fields:
            if field not in widget:
                self.errors.append(f"{prefix} Missing required field: {field}")

        # Widget type validation
        widget_type = widget.get("type")
        if widget_type and widget_type not in VALID_WIDGET_TYPES:
            self.errors.append(
                f"{prefix} Invalid widget type: '{widget_type}'. "
                f"Valid types: {VALID_WIDGET_TYPES}"
            )

        # Grid data validation
        grid_data = widget.get("gridData", {})
        if grid_data:
            self._validate_grid_data(prefix, grid_data)

        # Parameter validation
        params = widget.get("params", [])
        if params:
            self._validate_params(prefix, params)

        # Table-specific validation
        if widget_type == "table":
            self._validate_table_widget(prefix, widget)

        # Chart-specific validation
        if widget_type == "chart":
            self._validate_chart_widget(prefix, widget)

        # MCP tool matching validation
        if "mcp_tool" in widget:
            self._validate_mcp_tool(prefix, widget["mcp_tool"])

        # Refresh interval validation
        refetch = widget.get("refetchInterval")
        if refetch is not None:
            if not isinstance(refetch, (int, float, bool)):
                self.errors.append(
                    f"{prefix} refetchInterval must be number or false"
                )
            elif isinstance(refetch, (int, float)) and refetch < 1000:
                self.warnings.append(
                    f"{prefix} refetchInterval {refetch}ms is very low (min 1000ms)"
                )

    def _validate_grid_data(self, prefix: str, grid_data: Dict[str, Any]) -> None:
        """Validate grid layout data."""
        w = grid_data.get("w", 12)
        h = grid_data.get("h", 8)

        if not isinstance(w, (int, float)):
            self.errors.append(f"{prefix} gridData.w must be a number")
        elif not (10 <= w <= 40):
            self.warnings.append(
                f"{prefix} gridData.w={w} outside recommended range (10-40)"
            )

        if not isinstance(h, (int, float)):
            self.errors.append(f"{prefix} gridData.h must be a number")
        elif not (4 <= h <= 100):
            self.warnings.append(
                f"{prefix} gridData.h={h} outside recommended range (4-100)"
            )

        # Validate min/max if provided
        for key in ["minW", "maxW", "minH", "maxH"]:
            if key in grid_data:
                val = grid_data[key]
                if not isinstance(val, (int, float)):
                    self.errors.append(f"{prefix} gridData.{key} must be a number")

    def _validate_params(self, prefix: str, params: Any) -> None:
        """Validate widget parameters."""
        # Handle nested array format (parameter positioning)
        flat_params = []
        if isinstance(params, list):
            for p in params:
                if isinstance(p, list):
                    flat_params.extend(p)
                elif isinstance(p, dict):
                    flat_params.append(p)
        else:
            return

        for param in flat_params:
            if not isinstance(param, dict):
                continue

            param_name = param.get("paramName", "unknown")
            param_prefix = f"{prefix} param '{param_name}'"

            # Required param fields
            if "paramName" not in param:
                self.errors.append(f"{prefix} param missing paramName")
                continue

            param_type = param.get("type")
            if not param_type:
                self.errors.append(f"{param_prefix} missing type")
                continue

            if param_type not in VALID_PARAM_TYPES:
                self.errors.append(
                    f"{param_prefix} invalid type: '{param_type}'. "
                    f"Valid: {VALID_PARAM_TYPES}"
                )

            # Endpoint type requires optionsEndpoint
            if param_type == "endpoint":
                if "optionsEndpoint" not in param:
                    self.errors.append(
                        f"{param_prefix} (endpoint type) missing optionsEndpoint"
                    )

            # Static dropdown with options
            if param_type == "text" and "options" in param:
                options = param["options"]
                if not isinstance(options, list):
                    self.errors.append(f"{param_prefix} options must be an array")
                else:
                    for i, opt in enumerate(options):
                        if not isinstance(opt, dict):
                            self.errors.append(
                                f"{param_prefix} option[{i}] must be an object"
                            )
                        elif "value" not in opt:
                            self.errors.append(
                                f"{param_prefix} option[{i}] missing 'value'"
                            )

            # Date type with dynamic value
            if param_type == "date":
                value = param.get("value", "")
                if isinstance(value, str) and value.startswith("$"):
                    valid_modifiers = [
                        "$currentDate",
                        "$currentDate-",
                    ]
                    if not any(value.startswith(m) for m in valid_modifiers):
                        self.warnings.append(
                            f"{param_prefix} date modifier '{value}' may be invalid"
                        )

    def _validate_table_widget(self, prefix: str, widget: Dict[str, Any]) -> None:
        """Validate table-specific configuration."""
        data = widget.get("data", {})
        columns = data.get("columnsDefs", [])

        if not columns:
            # Columns are optional if they're inferred from data
            return

        if not isinstance(columns, list):
            self.errors.append(f"{prefix} data.columnsDefs must be an array")
            return

        fields_seen = set()
        for i, col in enumerate(columns):
            if not isinstance(col, dict):
                self.errors.append(f"{prefix} column[{i}] must be an object")
                continue

            field = col.get("field", f"column_{i}")
            col_prefix = f"{prefix} column '{field}'"

            if "field" not in col:
                self.errors.append(f"{prefix} column[{i}] missing 'field'")

            # Check for duplicate fields
            if field in fields_seen:
                self.warnings.append(f"{col_prefix} duplicate field name")
            fields_seen.add(field)

            # Validate cellDataType
            cell_type = col.get("cellDataType")
            if cell_type and cell_type not in VALID_CELL_DATA_TYPES:
                self.errors.append(
                    f"{col_prefix} invalid cellDataType: '{cell_type}'. "
                    f"Valid: {VALID_CELL_DATA_TYPES}"
                )

            # Validate chartDataType
            chart_type = col.get("chartDataType")
            if chart_type and chart_type not in VALID_CHART_DATA_TYPES:
                self.warnings.append(
                    f"{col_prefix} unknown chartDataType: '{chart_type}'"
                )

            # Validate formatterFn
            formatter = col.get("formatterFn")
            if formatter and formatter not in VALID_FORMATTER_FNS:
                self.warnings.append(
                    f"{col_prefix} unknown formatterFn: '{formatter}'"
                )

            # Validate renderFn
            render_fn = col.get("renderFn")
            if render_fn:
                render_fns = render_fn if isinstance(render_fn, list) else [render_fn]
                for fn in render_fns:
                    if fn not in VALID_RENDER_FNS:
                        self.warnings.append(
                            f"{col_prefix} unknown renderFn: '{fn}'"
                        )

            # Validate sparkline config
            if "sparkline" in col:
                self._validate_sparkline(col_prefix, col["sparkline"])

    def _validate_sparkline(self, prefix: str, sparkline: Dict[str, Any]) -> None:
        """Validate sparkline configuration."""
        valid_types = ["line", "area", "bar"]
        spark_type = sparkline.get("type")

        if spark_type and spark_type not in valid_types:
            self.warnings.append(
                f"{prefix} sparkline type '{spark_type}' should be one of: {valid_types}"
            )

        if "dataField" not in sparkline:
            self.warnings.append(f"{prefix} sparkline missing dataField")

    def _validate_chart_widget(self, prefix: str, widget: Dict[str, Any]) -> None:
        """Validate chart-specific configuration."""
        # Charts should support theme parameter
        params = widget.get("params", [])
        flat_params = []
        for p in params:
            if isinstance(p, list):
                flat_params.extend(p)
            elif isinstance(p, dict):
                flat_params.append(p)

        param_names = [p.get("paramName") for p in flat_params if isinstance(p, dict)]

        # theme is auto-injected, but good to be aware
        if "raw" in widget and widget["raw"]:
            # raw mode should be handled in endpoint
            pass

    def _validate_mcp_tool(self, prefix: str, mcp_tool: Dict[str, Any]) -> None:
        """Validate MCP tool matching configuration."""
        if "mcp_server" not in mcp_tool:
            self.errors.append(f"{prefix} mcp_tool missing 'mcp_server'")

        if "tool_id" not in mcp_tool:
            self.errors.append(f"{prefix} mcp_tool missing 'tool_id'")

    def report(self) -> None:
        """Print validation report to stdout."""
        print("\n" + "=" * 60)
        print("WIDGET VALIDATION REPORT")
        print("=" * 60)
        print(f"Path: {self.app_path}")
        print(f"Widgets found: {len(self.widget_ids)}")

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
        print("Usage: python validate_widgets.py <app_path>")
        print("Example: python validate_widgets.py apps/my-app/")
        sys.exit(1)

    app_path = Path(sys.argv[1])

    if not app_path.exists():
        print(f"Error: Path does not exist: {app_path}")
        sys.exit(1)

    if not app_path.is_dir():
        # If file passed, use parent directory
        app_path = app_path.parent

    validator = WidgetValidator(app_path)
    is_valid = validator.validate()
    validator.report()

    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
