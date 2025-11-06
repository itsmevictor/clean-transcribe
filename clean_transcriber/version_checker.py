"""Version checking utility to notify users of new releases."""
import urllib.request
import json
import click
from packaging import version
import os
import re


def get_current_version():
    """Get the current version of the package from setup.py."""
    try:
        # Try to find setup.py relative to this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        setup_path = os.path.join(os.path.dirname(current_dir), 'setup.py')

        if os.path.exists(setup_path):
            with open(setup_path, 'r') as f:
                content = f.read()
                match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    return match.group(1)
    except Exception:
        pass

    # Fallback version
    return "1.1.0"


def get_latest_pypi_version(package_name="clean-transcribe", timeout=2):
    """
    Fetch the latest version of the package from PyPI.

    Args:
        package_name: Name of the package on PyPI
        timeout: Request timeout in seconds

    Returns:
        Latest version string or None if fetch fails
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read().decode())
            return data['info']['version']
    except Exception:
        # Silently fail if we can't check for updates
        return None


def check_for_updates():
    """
    Check if a newer version is available on PyPI and display a message.
    This function is designed to fail gracefully and not interrupt the user experience.
    """
    try:
        current = get_current_version()
        latest = get_latest_pypi_version()

        if latest and version.parse(latest) > version.parse(current):
            click.secho(
                f"\n  A new version of clean-transcribe is available: {latest} (you have {current})",
                fg="yellow",
                bold=True
            )
            click.secho(
                f"  Update with: pip install --upgrade clean-transcribe\n",
                fg="yellow"
            )
    except Exception:
        # Silently fail - we don't want version checking to break the tool
        pass
