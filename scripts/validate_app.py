#!/usr/bin/env python3
"""
Unified app validator that runs both widgets and apps validation.

Usage:
    python scripts/validate_app.py <app_path>
    python scripts/validate_app.py apps/my-app/

Returns exit code 0 on success, 1 on any validation errors.
"""

import sys
import subprocess
from pathlib import Path


def run_validator(script_name: str, app_path: Path) -> tuple[bool, str]:
    """Run a validation script and return result."""
    script_path = Path(__file__).parent / script_name

    if not script_path.exists():
        return False, f"Script not found: {script_path}"

    try:
        result = subprocess.run(
            [sys.executable, str(script_path), str(app_path)],
            capture_output=True,
            text=True
        )
        output = result.stdout + result.stderr
        success = result.returncode == 0
        return success, output
    except Exception as e:
        return False, f"Error running {script_name}: {e}"


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python validate_app.py <app_path>")
        print("Example: python validate_app.py apps/my-app/")
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

    # Run widgets validation
    print("Running widgets.json validation...")
    widgets_ok, widgets_output = run_validator("validate_widgets.py", app_path)
    print(widgets_output)
    if not widgets_ok:
        all_passed = False

    # Run apps validation
    print("\nRunning apps.json validation...")
    apps_ok, apps_output = run_validator("validate_apps.py", app_path)
    print(apps_output)
    # apps.json is optional, so only fail if there are actual errors
    if "❌ ERRORS" in apps_output:
        all_passed = False

    # Final summary
    print("\n" + "=" * 60)
    print("FINAL RESULT")
    print("=" * 60)

    if all_passed:
        print("\n✅ All validations passed!")
        print("\nYour app is ready. Next steps:")
        print(f"  1. cd {app_path}")
        print("  2. pip install -r requirements.txt")
        print("  3. uvicorn main:app --reload --port 7779")
        print("  4. Add http://localhost:7779 to OpenBB Workspace")
    else:
        print("\n❌ Validation failed. Please fix the errors above.")

    print("\n" + "=" * 60)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
