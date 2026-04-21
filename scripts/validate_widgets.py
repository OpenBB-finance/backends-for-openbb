#!/usr/bin/env python3
"""
Validate widgets.json for OpenBB Workspace compatibility.

Usage:
    python scripts/validate_widgets.py <app_path>
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

VALID_WIDGET_TYPES = {
    "table",
    "chart",
    "table_ssrm",
    "markdown",
    "metric",
    "note",
    "multi_file_viewer",
    "live_grid",
    "newsfeed",
    "advanced-chart",
    "chart-highcharts",
    "youtube",
}

WIDGET_TYPE_ALIASES = {
    "advanced_charting": "advanced-chart",
    "ssrm_table": "table_ssrm",
}

VALID_PARAM_TYPES = {
    "text",
    "number",
    "boolean",
    "date",
    "endpoint",
    "ticker",
    "tabs",
    "form",
}

VALID_CELL_DATA_TYPES = {
    "text",
    "number",
    "boolean",
    "date",
    "dateString",
    "object",
}

VALID_CHART_DATA_TYPES = {
    "category",
    "series",
    "time",
    "excluded",
}

VALID_FORMATTER_FNS = {
    "int",
    "none",
    "percent",
    "normalized",
    "normalizedPercent",
    "dateToYear",
}

VALID_RENDER_FNS = {
    "greenRed",
    "titleCase",
    "hoverCard",
    "cellOnClick",
    "columnColor",
    "showCellChange",
}


def flatten_params(params: Any) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    if not isinstance(params, list):
        return flat
    for item in params:
        if isinstance(item, dict):
            flat.append(item)
        elif isinstance(item, list):
            flat.extend(p for p in item if isinstance(p, dict))
    return flat


class WidgetValidator:
    def __init__(self, app_path: Path):
        self.app_path = app_path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.widget_ids: set[str] = set()

    def validate(self) -> bool:
        widgets_path = self.app_path / "widgets.json"
        if not widgets_path.exists():
            self.errors.append(f"widgets.json not found at {widgets_path}")
            return False

        try:
            with open(widgets_path, "r", encoding="utf-8") as file:
                widgets = json.load(file)
        except json.JSONDecodeError as exc:
            self.errors.append(f"Invalid JSON: {exc}")
            return False

        if not isinstance(widgets, dict):
            self.errors.append(
                "widgets.json must be an OBJECT with widget IDs as keys"
            )
            return False

        self.widget_ids = set(widgets.keys())

        for widget_id, widget in widgets.items():
            if not isinstance(widget, dict):
                self.errors.append(f"[{widget_id}] Widget definition must be an object")
                continue
            self._validate_widget(widget_id, widget)

        return not self.errors

    def _validate_widget(self, widget_id: str, widget: dict[str, Any]) -> None:
        prefix = f"[{widget_id}]"

        for field in ("name", "type", "endpoint"):
            if field not in widget:
                self.errors.append(f"{prefix} Missing required field: {field}")

        widget_type = widget.get("type")
        if isinstance(widget_type, str):
            if widget_type in WIDGET_TYPE_ALIASES:
                self.errors.append(
                    f"{prefix} Invalid widget type '{widget_type}'. "
                    f"Use '{WIDGET_TYPE_ALIASES[widget_type]}' instead."
                )
            elif widget_type not in VALID_WIDGET_TYPES:
                self.errors.append(
                    f"{prefix} Invalid widget type '{widget_type}'. "
                    f"Valid types: {sorted(VALID_WIDGET_TYPES)}"
                )

        grid_data = widget.get("gridData")
        if grid_data is not None:
            self._validate_grid_data(prefix, grid_data)

        params = widget.get("params")
        if params is not None:
            self._validate_params(prefix, params)

        source = widget.get("source")
        if source is not None and (
            not isinstance(source, list) or not all(isinstance(item, str) for item in source)
        ):
            self.errors.append(f"{prefix} source must be an array of strings")

        if widget_type == "table":
            self._validate_table_widget(prefix, widget)

        if widget_type == "chart" and widget.get("raw") not in (None, True, False):
            self.errors.append(f"{prefix} raw must be a boolean when provided")

        if "mcp_tool" in widget:
            self._validate_mcp_tool(prefix, widget["mcp_tool"])

        refetch = widget.get("refetchInterval")
        if refetch is not None:
            if not isinstance(refetch, (int, float, bool)):
                self.errors.append(f"{prefix} refetchInterval must be number or false")
            elif isinstance(refetch, (int, float)) and refetch < 1000:
                self.warnings.append(
                    f"{prefix} refetchInterval {refetch}ms is very low"
                )

    def _validate_grid_data(self, prefix: str, grid_data: Any) -> None:
        if not isinstance(grid_data, dict):
            self.errors.append(f"{prefix} gridData must be an object")
            return

        for key in ("w", "h", "minW", "maxW", "minH", "maxH"):
            if key in grid_data and not isinstance(grid_data[key], (int, float)):
                self.errors.append(f"{prefix} gridData.{key} must be a number")

        w = grid_data.get("w")
        h = grid_data.get("h")
        if isinstance(w, (int, float)) and not (10 <= w <= 40):
            self.warnings.append(f"{prefix} gridData.w={w} outside recommended range")
        if isinstance(h, (int, float)) and not (4 <= h <= 100):
            self.warnings.append(f"{prefix} gridData.h={h} outside recommended range")

    def _validate_params(self, prefix: str, params: Any) -> None:
        for param in flatten_params(params):
            if "paramName" not in param:
                self.errors.append(f"{prefix} param missing paramName")
                continue

            param_name = param["paramName"]
            param_prefix = f"{prefix} param '{param_name}'"
            param_type = param.get("type")

            if param_type not in VALID_PARAM_TYPES:
                self.errors.append(
                    f"{param_prefix} invalid type '{param_type}'. "
                    f"Valid: {sorted(VALID_PARAM_TYPES)}"
                )
                continue

            if param_type == "endpoint" and "optionsEndpoint" not in param:
                self.errors.append(
                    f"{param_prefix} missing optionsEndpoint for endpoint param"
                )

            if "options" in param and not isinstance(param["options"], list):
                self.errors.append(f"{param_prefix} options must be an array")

            if isinstance(param.get("options"), list):
                for idx, option in enumerate(param["options"]):
                    if not isinstance(option, dict):
                        self.errors.append(
                            f"{param_prefix} option[{idx}] must be an object"
                        )
                    elif "value" not in option:
                        self.errors.append(
                            f"{param_prefix} option[{idx}] missing value"
                        )

            value = param.get("value")
            if param_type == "date" and isinstance(value, str) and value.startswith("$"):
                if not (
                    value.startswith("$currentDate-")
                    or value.startswith("$currentDate+")
                    or value == "$currentDate"
                ):
                    self.warnings.append(
                        f"{param_prefix} uses an unrecognized date modifier '{value}'"
                    )

    def _validate_table_widget(self, prefix: str, widget: dict[str, Any]) -> None:
        data = widget.get("data", {})
        if data and not isinstance(data, dict):
            self.errors.append(f"{prefix} data must be an object")
            return

        if isinstance(data, dict) and "columnsDefs" in data:
            self.errors.append(
                f"{prefix} data.columnsDefs is invalid; use data.table.columnsDefs"
            )

        if "columns" in widget:
            self.errors.append(
                f"{prefix} columns is invalid; use data.table.columnsDefs"
            )

        table = data.get("table", {}) if isinstance(data, dict) else {}
        if table and not isinstance(table, dict):
            self.errors.append(f"{prefix} data.table must be an object")
            return

        formatter = table.get("formatterFn")
        if formatter and formatter not in VALID_FORMATTER_FNS:
            self.warnings.append(
                f"{prefix} data.table.formatterFn '{formatter}' is not recognized"
            )

        columns = table.get("columnsDefs", [])
        if not columns:
            return
        if not isinstance(columns, list):
            self.errors.append(f"{prefix} data.table.columnsDefs must be an array")
            return

        seen_fields: set[str] = set()
        for idx, column in enumerate(columns):
            if not isinstance(column, dict):
                self.errors.append(f"{prefix} column[{idx}] must be an object")
                continue

            field = column.get("field", f"column_{idx}")
            column_prefix = f"{prefix} column '{field}'"

            if "field" not in column:
                self.errors.append(f"{prefix} column[{idx}] missing field")

            if field in seen_fields:
                self.warnings.append(f"{column_prefix} duplicates a previous field")
            seen_fields.add(field)

            cell_data_type = column.get("cellDataType")
            if cell_data_type and cell_data_type not in VALID_CELL_DATA_TYPES:
                self.errors.append(
                    f"{column_prefix} invalid cellDataType '{cell_data_type}'"
                )

            chart_data_type = column.get("chartDataType")
            if chart_data_type and chart_data_type not in VALID_CHART_DATA_TYPES:
                self.warnings.append(
                    f"{column_prefix} unknown chartDataType '{chart_data_type}'"
                )

            formatter_fn = column.get("formatterFn")
            if formatter_fn and formatter_fn not in VALID_FORMATTER_FNS:
                self.warnings.append(
                    f"{column_prefix} unknown formatterFn '{formatter_fn}'"
                )

            render_fn = column.get("renderFn")
            render_fns = []
            if isinstance(render_fn, str):
                render_fns = [render_fn]
            elif isinstance(render_fn, list):
                render_fns = [fn for fn in render_fn if isinstance(fn, str)]

            for fn in render_fns:
                if fn not in VALID_RENDER_FNS:
                    self.warnings.append(f"{column_prefix} unknown renderFn '{fn}'")

            if "cellOnClick" in render_fns:
                params = column.get("renderFnParams")
                if not isinstance(params, dict):
                    self.errors.append(
                        f"{column_prefix} renderFnParams must be an object for cellOnClick"
                    )
                else:
                    if "groupByParamName" in params:
                        self.errors.append(
                            f"{column_prefix} uses deprecated groupByParamName; "
                            "use renderFnParams.groupBy.paramName"
                        )
                    if params.get("actionType") == "groupBy":
                        group_by = params.get("groupBy")
                        if not isinstance(group_by, dict):
                            self.errors.append(
                                f"{column_prefix} renderFnParams.groupBy must be an object"
                            )
                        elif "paramName" not in group_by:
                            self.errors.append(
                                f"{column_prefix} renderFnParams.groupBy missing paramName"
                            )

            if "sparkline" in column:
                self._validate_sparkline(column_prefix, column["sparkline"])

    def _validate_sparkline(self, prefix: str, sparkline: Any) -> None:
        if not isinstance(sparkline, dict):
            self.errors.append(f"{prefix} sparkline must be an object")
            return

        spark_type = sparkline.get("type")
        if spark_type and spark_type not in {"line", "area", "bar"}:
            self.warnings.append(f"{prefix} sparkline type '{spark_type}' is unknown")

    def _validate_mcp_tool(self, prefix: str, mcp_tool: Any) -> None:
        if not isinstance(mcp_tool, dict):
            self.errors.append(f"{prefix} mcp_tool must be an object")
            return
        if "mcp_server" not in mcp_tool:
            self.errors.append(f"{prefix} mcp_tool missing mcp_server")
        if "tool_id" not in mcp_tool:
            self.errors.append(f"{prefix} mcp_tool missing tool_id")

    def report(self) -> None:
        print("\n" + "=" * 60)
        print("WIDGET VALIDATION REPORT")
        print("=" * 60)
        print(f"Path: {self.app_path}")
        print(f"Widgets found: {len(self.widget_ids)}")

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
        print("Usage: python validate_widgets.py <app_path>")
        sys.exit(1)

    app_path = Path(sys.argv[1])
    if not app_path.exists():
        print(f"Error: Path does not exist: {app_path}")
        sys.exit(1)
    if not app_path.is_dir():
        app_path = app_path.parent

    validator = WidgetValidator(app_path)
    is_valid = validator.validate()
    validator.report()
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
