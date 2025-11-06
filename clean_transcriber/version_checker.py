"""Version checking utility to notify users of new releases."""
import urllib.request
import json
import click
from packaging import version
import os
import re
import time
from pathlib import Path


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


def get_cache_dir():
    """Get the cache directory for storing version check data."""
    # Try XDG cache directory first (Linux/Mac standard)
    xdg_cache = os.environ.get('XDG_CACHE_HOME')
    if xdg_cache:
        cache_dir = Path(xdg_cache) / 'clean-transcribe'
    else:
        # Fallback to ~/.cache/clean-transcribe
        cache_dir = Path.home() / '.cache' / 'clean-transcribe'

    # Create directory if it doesn't exist
    try:
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    except Exception:
        # If we can't create the cache directory, return None
        return None


def get_cache_file_path():
    """Get the path to the version check cache file."""
    cache_dir = get_cache_dir()
    if cache_dir:
        return cache_dir / 'version_check.json'
    return None


def read_cache(cache_file, check_interval_hours=24):
    """
    Read the cache file and check if it's still valid.

    Args:
        cache_file: Path to the cache file
        check_interval_hours: How many hours the cache is valid for

    Returns:
        Cached data dict if valid, None otherwise
    """
    try:
        if cache_file and cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                last_check = data.get('last_check', 0)
                current_time = time.time()

                # Check if cache is still valid
                if current_time - last_check < (check_interval_hours * 3600):
                    return data
    except Exception:
        pass
    return None


def write_cache(cache_file, latest_version):
    """
    Write the cache file with the latest check data.

    Args:
        cache_file: Path to the cache file
        latest_version: The latest version from PyPI
    """
    try:
        if cache_file:
            data = {
                'last_check': time.time(),
                'latest_version': latest_version
            }
            with open(cache_file, 'w') as f:
                json.dump(data, f)
    except Exception:
        # Silently fail if we can't write the cache
        pass


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


def check_for_updates(check_interval_hours=24):
    """
    Check if a newer version is available on PyPI and display a message.
    Uses a cache to avoid checking too frequently (default: once per 24 hours).
    This function is designed to fail gracefully and not interrupt the user experience.

    Args:
        check_interval_hours: How many hours to wait between checks (default: 24)
    """
    try:
        current = get_current_version()
        cache_file = get_cache_file_path()

        # Try to read from cache first
        cached_data = read_cache(cache_file, check_interval_hours)

        if cached_data:
            # Use cached version data
            latest = cached_data.get('latest_version')
        else:
            # Cache expired or doesn't exist, check PyPI
            latest = get_latest_pypi_version()

            # Update cache with the new data
            if latest:
                write_cache(cache_file, latest)

        # Display notification if a newer version is available
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
