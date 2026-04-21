#!/usr/bin/env python3
"""
Validate widget endpoints and core backend endpoints.

Usage:
    python scripts/validate_endpoints.py <app_path> [--base-url URL]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests


WIDGET_TYPE_VALIDATORS = {
    "table": lambda response: isinstance(response, list),
    "chart": lambda response: isinstance(response, dict)
    and ("data" in response or "layout" in response),
    "table_ssrm": lambda response: isinstance(response, dict) and "rowData" in response,
    "metric": lambda response: isinstance(response, list)
    and all(isinstance(item, dict) and "label" in item and "value" in item for item in response),
    "markdown": lambda response: isinstance(response, str),
    "note": lambda response: isinstance(response, str),
    "newsfeed": lambda response: isinstance(response, list)
    and all(isinstance(item, dict) and "title" in item for item in response),
    "multi_file_viewer": lambda response: isinstance(response, list),
    "live_grid": lambda response: isinstance(response, list),
    "advanced-chart": lambda response: True,
    "chart-highcharts": lambda response: isinstance(response, dict),
    "youtube": lambda response: isinstance(response, (str, dict)),
}

POST_WIDGET_TYPES = {"multi_file_viewer", "table_ssrm"}
TEXT_WIDGET_TYPES = {"markdown", "note", "youtube"}


class EndpointValidator:
    def __init__(self, app_path: Path, base_url: str):
        self.app_path = app_path
        self.base_url = base_url.rstrip("/")
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.results: list[dict[str, Any]] = []
        self.widgets: list[dict[str, Any]] = []

    def load_widgets(self) -> bool:
        widgets_path = self.app_path / "widgets.json"
        if not widgets_path.exists():
            self.errors.append(f"widgets.json not found at {widgets_path}")
            return False

        try:
            with open(widgets_path, "r", encoding="utf-8") as file:
                widgets = json.load(file)
        except json.JSONDecodeError as exc:
            self.errors.append(f"Invalid JSON in widgets.json: {exc}")
            return False

        if not isinstance(widgets, dict):
            self.errors.append("widgets.json must be an object keyed by widget id")
            return False

        self.widgets = []
        for widget_id, widget in widgets.items():
            if isinstance(widget, dict):
                item = dict(widget)
                item["widgetId"] = widget_id
                self.widgets.append(item)

        return True

    def check_server_running(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/widgets.json", timeout=5)
            return response.status_code < 500
        except requests.RequestException:
            return False

    def validate_all(self) -> bool:
        if not self.check_server_running():
            self.errors.append(
                f"Server not reachable at {self.base_url}. Start with: uvicorn main:app --port 7779"
            )
            return False

        if not self.load_widgets():
            return False

        self.validate_core_endpoints()

        for widget in self.widgets:
            success, message, elapsed_ms = self.validate_endpoint(widget)
            self.results.append(
                {
                    "widget_id": widget.get("widgetId", "unknown"),
                    "endpoint": widget.get("endpoint", ""),
                    "type": widget.get("type", "unknown"),
                    "success": success,
                    "message": message,
                    "time_ms": elapsed_ms,
                }
            )
            if not success:
                self.errors.append(f"[{widget.get('widgetId', 'unknown')}] {message}")

        return not self.errors

    def validate_core_endpoints(self) -> None:
        self._validate_core_widgets()
        self._validate_core_apps()

    def _validate_core_widgets(self) -> None:
        url = f"{self.base_url}/widgets.json"
        start = time.time()
        try:
            response = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000
            if response.status_code != 200:
                self.results.append(
                    {
                        "widget_id": "/widgets.json",
                        "endpoint": "/widgets.json",
                        "type": "core",
                        "success": False,
                        "message": f"HTTP {response.status_code}",
                        "time_ms": elapsed,
                    }
                )
                self.errors.append(f"/widgets.json returns HTTP {response.status_code}")
                return

            data = response.json()
            success = isinstance(data, dict)
            self.results.append(
                {
                    "widget_id": "/widgets.json",
                    "endpoint": "/widgets.json",
                    "type": "core",
                    "success": success,
                    "message": "OK" if success else "widgets.json must return an object",
                    "time_ms": elapsed,
                }
            )
            if not success:
                self.errors.append("/widgets.json must return an object")
        except (requests.RequestException, json.JSONDecodeError) as exc:
            self.results.append(
                {
                    "widget_id": "/widgets.json",
                    "endpoint": "/widgets.json",
                    "type": "core",
                    "success": False,
                    "message": str(exc),
                    "time_ms": None,
                }
            )
            self.errors.append(f"/widgets.json error: {exc}")

    def _validate_core_apps(self) -> None:
        url = f"{self.base_url}/apps.json"
        start = time.time()
        try:
            response = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000

            if response.status_code == 404:
                self.results.append(
                    {
                        "widget_id": "/apps.json",
                        "endpoint": "/apps.json",
                        "type": "core",
                        "success": True,
                        "message": "Not found (optional)",
                        "time_ms": elapsed,
                    }
                )
                self.warnings.append("/apps.json not found (optional endpoint)")
                return

            if response.status_code != 200:
                self.results.append(
                    {
                        "widget_id": "/apps.json",
                        "endpoint": "/apps.json",
                        "type": "core",
                        "success": False,
                        "message": f"HTTP {response.status_code}",
                        "time_ms": elapsed,
                    }
                )
                self.errors.append(f"/apps.json returns HTTP {response.status_code}")
                return

            data = response.json()
            success = isinstance(data, list)
            self.results.append(
                {
                    "widget_id": "/apps.json",
                    "endpoint": "/apps.json",
                    "type": "core",
                    "success": success,
                    "message": "OK" if success else "apps.json must return an array",
                    "time_ms": elapsed,
                }
            )
            if not success:
                self.errors.append("/apps.json must return an array")
        except (requests.RequestException, json.JSONDecodeError) as exc:
            self.results.append(
                {
                    "widget_id": "/apps.json",
                    "endpoint": "/apps.json",
                    "type": "core",
                    "success": False,
                    "message": str(exc),
                    "time_ms": None,
                }
            )
            self.errors.append(f"/apps.json error: {exc}")

    def validate_endpoint(self, widget: dict[str, Any]) -> tuple[bool, str, float | None]:
        widget_id = widget.get("widgetId", "unknown")
        endpoint = widget.get("endpoint")
        widget_type = widget.get("type", "unknown")

        if not endpoint:
            return False, "No endpoint defined", None

        url = urljoin(self.base_url + "/", str(endpoint).lstrip("/"))
        method = "POST" if widget_type in POST_WIDGET_TYPES else "GET"
        params = self._collect_params(widget)

        try:
            start = time.time()
            if method == "POST":
                response = requests.post(url, json=params, timeout=30)
            else:
                response = requests.get(url, params=params, timeout=30)
            elapsed = (time.time() - start) * 1000

            if response.status_code != 200:
                return False, f"HTTP {response.status_code}: {response.text[:100]}", elapsed

            try:
                data = response.json()
            except json.JSONDecodeError:
                if widget_type in TEXT_WIDGET_TYPES:
                    return True, "OK (non-JSON response)", elapsed
                return False, "Invalid JSON response", elapsed

            validator = WIDGET_TYPE_VALIDATORS.get(widget_type)
            if validator and not validator(data):
                return False, f"Invalid response format for {widget_type}", elapsed

            return True, "OK", elapsed
        except requests.RequestException as exc:
            return False, str(exc), None

    def _collect_params(self, widget: dict[str, Any]) -> dict[str, Any]:
        params: dict[str, Any] = {}
        raw_params = widget.get("params", [])
        if not isinstance(raw_params, list):
            return params
        for item in raw_params:
            if isinstance(item, dict) and "paramName" in item:
                params[item["paramName"]] = item.get("value", "")
            elif isinstance(item, list):
                for subitem in item:
                    if isinstance(subitem, dict) and "paramName" in subitem:
                        params[subitem["paramName"]] = subitem.get("value", "")
        return params

    def report(self) -> None:
        print("\n" + "=" * 70)
        print("ENDPOINT VALIDATION REPORT")
        print("=" * 70)
        print(f"App Path: {self.app_path}")
        print(f"Base URL: {self.base_url}")
        print(f"Widgets: {len(self.widgets)}")

        passed = sum(1 for result in self.results if result["success"])
        failed = len(self.results) - passed
        print(f"\nResults: {passed} passed, {failed} failed")

        print("\n" + "-" * 70)
        print("ENDPOINT RESULTS")
        print("-" * 70)
        for result in self.results:
            status = "[OK]" if result["success"] else "[FAIL]"
            time_str = f"{result['time_ms']:.0f}ms" if result["time_ms"] else "N/A"
            print(
                f"{status} [{result['type']:15}] "
                f"{result['widget_id']:25} {time_str:8} {result['message']}"
            )

        if self.errors:
            print("\n" + "-" * 70)
            print(f"[ERRORS] ({len(self.errors)})")
            print("-" * 70)
            for error in self.errors:
                print(f"  - {error}")

        if self.warnings:
            print("\n" + "-" * 70)
            print(f"[WARNINGS] ({len(self.warnings)})")
            print("-" * 70)
            for warning in self.warnings:
                print(f"  - {warning}")

        print("\n" + "=" * 70)
        print("[OK] All endpoints validated successfully!" if not self.errors else "[FAIL] Endpoint validation failed. Fix errors and retry.")
        print("=" * 70)


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate OpenBB app endpoints")
    parser.add_argument("app_path", type=Path, help="Path to the app directory")
    parser.add_argument(
        "--base-url",
        default="http://localhost:7779",
        help="Base URL of the running backend",
    )
    args = parser.parse_args()

    if not args.app_path.exists():
        print(f"Error: Path does not exist: {args.app_path}")
        sys.exit(1)
    if not args.app_path.is_dir():
        args.app_path = args.app_path.parent

    validator = EndpointValidator(args.app_path, args.base_url)
    is_valid = validator.validate_all()
    validator.report()
    sys.exit(0 if is_valid else 1)


if __name__ == "__main__":
    main()
