#!/usr/bin/env python3
"""
Run both widgets and apps validation scripts.

Usage:
    python scripts/validate_app.py <app_path>
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_validator(script_name: str, app_path: Path) -> tuple[bool, str]:
    script_path = Path(__file__).parent / script_name
    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(app_path)],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as exc:
        return False, f"Error running {script_name}: {exc}"


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python validate_app.py <app_path>")
        sys.exit(1)

    app_path = Path(sys.argv[1])
    if not app_path.exists():
        print(f"Error: Path does not exist: {app_path}")
        sys.exit(1)
    if not app_path.is_dir():
        app_path = app_path.parent

    print("=" * 60)
    print("OPENBB APP VALIDATION")
    print("=" * 60)
    print(f"App Path: {app_path}")
    print()

    all_passed = True

    print("Running widgets.json validation...")
    widgets_ok, widgets_output = run_validator("validate_widgets.py", app_path)
    print(widgets_output)
    if not widgets_ok:
        all_passed = False

    print("\nRunning apps.json validation...")
    apps_ok, apps_output = run_validator("validate_apps.py", app_path)
    print(apps_output)
    if "[ERRORS]" in apps_output:
        all_passed = False

    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    if all_passed:
        print("\n[OK] All validations passed!")
        print("\nYour app is ready. Next steps:")
        print(f"  1. cd {app_path}")
        print("  2. pip install -r requirements.txt")
        print("  3. uvicorn main:app --reload --port 7779")
        print("  4. Add http://localhost:7779 to OpenBB Workspace")
    else:
        print("\n[FAIL] Validation failed. Please fix the errors above.")

    print("\n" + "=" * 60)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
