"""
Version information for knitout_interpreter.

This module provides version information by reading from the installed package
metadata, ensuring a single source of truth with pyproject.toml.
"""

try:
    # Python 3.8+ standard library
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    try:
        # Fallback for Python < 3.8 (importlib_resources is already a dependency)
        from importlib_metadata import version, PackageNotFoundError
    except ImportError:
        # If neither is available, define a minimal fallback
        def version(package_name: str) -> str:
            return "0.0.0+unknown"

        class PackageNotFoundError(Exception):
            pass

try:
    # Get version from installed package metadata
    # This reads from pyproject.toml when the package is installed
    __version__ = version("knitout-interpreter")
except PackageNotFoundError:
    # Package is not installed (e.g., during development)
    # This happens when running from source without installation
    __version__ = "0.0.0+dev"

# Make version available for import
__all__ = ["__version__"]