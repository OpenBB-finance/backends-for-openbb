#!/usr/bin/env python3
"""
Validate that all widget endpoints are reachable and return valid data.

Usage:
    python scripts/validate_endpoints.py <app_path> [--base-url URL]
    python scripts/validate_endpoints.py apps/my-app/
    python scripts/validate_endpoints.py apps/my-app/ --base-url http://localhost:7779

This script:
1. Reads widgets.json to get endpoint definitions
2. Makes HTTP requests to each endpoint
3. Validates response format matches widget type
4. Reports success/failure for each endpoint

Returns exit code 0 on success, 1 on validation errors.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)


# Expected response formats by widget type
WIDGET_TYPE_VALIDATORS = {
    "table": lambda r: isinstance(r, list),
    "chart": lambda r: isinstance(r, dict) and ("data" in r or "layout" in r),
    "metric": lambda r: isinstance(r, list) and all(
        isinstance(m, dict) and "label" in m and "value" in m for m in r
    ),
    "markdown": lambda r: isinstance(r, str),
    "newsfeed": lambda r: isinstance(r, list) and all(
        isinstance(a, dict) and "title" in a for a in r
    ),
    "html": lambda r: isinstance(r, str) or (isinstance(r, dict) and "content" in r),
    "pdf": lambda r: isinstance(r, dict) and "data_format" in r,
    "multi_file_viewer": lambda r: isinstance(r, list),
    "omni": lambda r: isinstance(r, dict) and "data_format" in r,
    "ssrm_table": lambda r: isinstance(r, dict) and "rowData" in r,
    "advanced_charting": lambda r: True,  # UDF has multiple endpoints
    "chart-highcharts": lambda r: isinstance(r, dict),
    "live_grid": lambda r: isinstance(r, list),
}


class EndpointValidator:
    """Validates widget endpoints by making HTTP requests."""

    def __init__(self, app_path: Path, base_url: str = "http://localhost:7779"):
        self.app_path = app_path
        self.base_url = base_url.rstrip("/")
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.results: List[Dict[str, Any]] = []
        self.widgets: List[Dict[str, Any]] = []

    def load_widgets(self) -> bool:
        """Load widgets from widgets.json."""
        widgets_path = self.app_path / "widgets.json"

        if not widgets_path.exists():
            self.errors.append(f"widgets.json not found at {widgets_path}")
            return False

        try:
            with open(widgets_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, list):
                self.widgets = data
            elif isinstance(data, dict):
                self.widgets = list(data.values())
            else:
                self.errors.append("widgets.json must be array or object")
                return False

            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in widgets.json: {e}")
            return False

    def check_server_running(self) -> bool:
        """Check if the backend server is running."""
        try:
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            return False
        except requests.exceptions.Timeout:
            return False

    def validate_endpoint(
        self,
        widget: Dict[str, Any]
    ) -> Tuple[bool, str, Optional[float]]:
        """
        Validate a single widget endpoint.

        Returns:
            Tuple of (success, message, response_time_ms)
        """
        widget_id = widget.get("widgetId", widget.get("endpoint", "unknown"))
        endpoint = widget.get("endpoint", "")
        widget_type = widget.get("type", "unknown")

        if not endpoint:
            return False, "No endpoint defined", None

        # Build URL
        url = urljoin(self.base_url + "/", endpoint.lstrip("/"))

        # Determine HTTP method
        # POST widgets: omni, multi_file_viewer, ssrm_table
        method = "POST" if widget_type in ["omni", "multi_file_viewer", "ssrm_table"] else "GET"

        # Build request params
        params = {}
        for param in widget.get("params", []):
            if isinstance(param, list):
                for p in param:
                    if isinstance(p, dict) and "paramName" in p:
                        params[p["paramName"]] = p.get("value", "")
            elif isinstance(param, dict) and "paramName" in param:
                params[param["paramName"]] = param.get("value", "")

        try:
            start_time = time.time()

            if method == "POST":
                response = requests.post(url, json=params, timeout=30)
            else:
                response = requests.get(url, params=params, timeout=30)

            elapsed_ms = (time.time() - start_time) * 1000

            # Check status code
            if response.status_code != 200:
                return (
                    False,
                    f"HTTP {response.status_code}: {response.text[:100]}",
                    elapsed_ms
                )

            # Try to parse JSON
            try:
                data = response.json()
            except json.JSONDecodeError:
                # Some widgets return non-JSON (HTML, markdown)
                if widget_type in ["html", "markdown"]:
                    return True, "OK (non-JSON response)", elapsed_ms
                return False, "Invalid JSON response", elapsed_ms

            # Validate response format
            validator = WIDGET_TYPE_VALIDATORS.get(widget_type)
            if validator:
                if not validator(data):
                    return (
                        False,
                        f"Invalid response format for {widget_type} widget",
                        elapsed_ms
                    )

            # Check for empty data
            if isinstance(data, list) and len(data) == 0:
                return True, "OK (empty array)", elapsed_ms
            if isinstance(data, dict) and not data:
                return True, "OK (empty object)", elapsed_ms

            return True, "OK", elapsed_ms

        except requests.exceptions.ConnectionError:
            return False, "Connection refused", None
        except requests.exceptions.Timeout:
            return False, "Request timeout (>30s)", None
        except Exception as e:
            return False, f"Error: {str(e)}", None

    def validate_core_endpoints(self) -> None:
        """Validate core /widgets.json and /apps.json endpoints."""
        # Check /widgets.json
        try:
            url = f"{self.base_url}/widgets.json"
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, (list, dict)):
                        self.results.append({
                            "widget_id": "/widgets.json",
                            "endpoint": "/widgets.json",
                            "type": "core",
                            "success": True,
                            "message": f"OK ({len(data) if isinstance(data, list) else len(data.keys())} widgets)",
                            "time_ms": elapsed
                        })
                    else:
                        self.results.append({
                            "widget_id": "/widgets.json",
                            "endpoint": "/widgets.json",
                            "type": "core",
                            "success": False,
                            "message": "Invalid format",
                            "time_ms": elapsed
                        })
                        self.errors.append("/widgets.json returns invalid format")
                except json.JSONDecodeError:
                    self.results.append({
                        "widget_id": "/widgets.json",
                        "endpoint": "/widgets.json",
                        "type": "core",
                        "success": False,
                        "message": "Invalid JSON",
                        "time_ms": elapsed
                    })
                    self.errors.append("/widgets.json returns invalid JSON")
            else:
                self.results.append({
                    "widget_id": "/widgets.json",
                    "endpoint": "/widgets.json",
                    "type": "core",
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "time_ms": elapsed
                })
                self.errors.append(f"/widgets.json returns HTTP {response.status_code}")
        except Exception as e:
            self.results.append({
                "widget_id": "/widgets.json",
                "endpoint": "/widgets.json",
                "type": "core",
                "success": False,
                "message": str(e),
                "time_ms": None
            })
            self.errors.append(f"/widgets.json error: {e}")

        # Check /apps.json (optional)
        try:
            url = f"{self.base_url}/apps.json"
            start = time.time()
            response = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000

            if response.status_code == 200:
                self.results.append({
                    "widget_id": "/apps.json",
                    "endpoint": "/apps.json",
                    "type": "core",
                    "success": True,
                    "message": "OK",
                    "time_ms": elapsed
                })
            elif response.status_code == 404:
                self.results.append({
                    "widget_id": "/apps.json",
                    "endpoint": "/apps.json",
                    "type": "core",
                    "success": True,
                    "message": "Not found (optional)",
                    "time_ms": elapsed
                })
                self.warnings.append("/apps.json not found (optional endpoint)")
            else:
                self.results.append({
                    "widget_id": "/apps.json",
                    "endpoint": "/apps.json",
                    "type": "core",
                    "success": False,
                    "message": f"HTTP {response.status_code}",
                    "time_ms": elapsed
                })
        except Exception as e:
            self.warnings.append(f"/apps.json error: {e}")

    def validate_all(self) -> bool:
        """Run all endpoint validations."""
        # Check server is running
        if not self.check_server_running():
            self.errors.append(
                f"Server not running at {self.base_url}. "
                "Start with: uvicorn main:app --port 7779"
            )
            return False

        # Load widgets
        if not self.load_widgets():
            return False

        # Validate core endpoints
        self.validate_core_endpoints()

        # Validate each widget endpoint
        for widget in self.widgets:
            widget_id = widget.get("widgetId", widget.get("endpoint", "unknown"))
            endpoint = widget.get("endpoint", "")
            widget_type = widget.get("type", "unknown")

            success, message, time_ms = self.validate_endpoint(widget)

            self.results.append({
                "widget_id": widget_id,
                "endpoint": endpoint,
                "type": widget_type,
                "success": success,
                "message": message,
                "time_ms": time_ms
            })

            if not success:
                self.errors.append(f"[{widget_id}] {message}")

        return len(self.errors) == 0

    def report(self) -> None:
        """Print validation report."""
        print("\n" + "=" * 70)
        print("ENDPOINT VALIDATION REPORT")
        print("=" * 70)
        print(f"App Path: {self.app_path}")
        print(f"Base URL: {self.base_url}")
        print(f"Widgets: {len(self.widgets)}")

        # Summary
        passed = sum(1 for r in self.results if r["success"])
        failed = len(self.results) - passed

        print(f"\nResults: {passed} passed, {failed} failed")

        # Detailed results
        print("\n" + "-" * 70)
        print("ENDPOINT RESULTS")
        print("-" * 70)

        for result in self.results:
            status = "✅" if result["success"] else "❌"
            time_str = f"{result['time_ms']:.0f}ms" if result["time_ms"] else "N/A"

            print(
                f"{status} [{result['type']:15}] "
                f"{result['widget_id']:25} "
                f"{time_str:8} "
                f"{result['message']}"
            )

        # Errors
        if self.errors:
            print("\n" + "-" * 70)
            print(f"❌ ERRORS ({len(self.errors)})")
            print("-" * 70)
            for error in self.errors:
                print(f"   • {error}")

        # Warnings
        if self.warnings:
            print("\n" + "-" * 70)
            print(f"⚠️  WARNINGS ({len(self.warnings)})")
            print("-" * 70)
            for warning in self.warnings:
                print(f"   • {warning}")

        # Final status
        print("\n" + "=" * 70)
        if not self.errors:
            print("✅ All endpoints validated successfully!")
        else:
            print("❌ Endpoint validation failed. Fix errors and retry.")
        print("=" * 70)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate OpenBB app endpoints"
    )
    parser.add_argument(
        "app_path",
        type=Path,
        help="Path to the app directory"
    )
    parser.add_argument(
        "--base-url",
        default="http://localhost:7779",
        help="Base URL of the running backend (default: http://localhost:7779)"
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
