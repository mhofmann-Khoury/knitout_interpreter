#!/usr/bin/env python3
"""
Script to automatically generate Sphinx API documentation from source code.
This script uses sphinx-apidoc to automatically create RST files for all modules.
"""

import subprocess
import sys
from pathlib import Path


def run_sphinx_apidoc():
    """Use sphinx-apidoc to automatically generate API documentation."""

    # Get paths
    docs_dir = Path(__file__).parent
    source_dir = docs_dir / "source"
    api_dir = source_dir / "api"
    src_dir = docs_dir.parent / "src" / "knitout_interpreter"

    # Ensure API directory exists
    api_dir.mkdir(exist_ok=True)

    # Run sphinx-apidoc command
    cmd = [
        "poetry", "run", "sphinx-apidoc",
        "-o", str(api_dir),  # Output directory
        str(src_dir),  # Source directory
        "--force",  # Overwrite existing files
        "--module-first",  # Module docs before submodules
        "--separate",  # Separate page for each module
        "--tocfile", "modules",  # Name of TOC file
        "--maxdepth", "4",  # Maximum depth of submodules
    ]

    print("🤖 Running sphinx-apidoc to generate API documentation...")
    print(f"📁 Source: {src_dir}")
    print(f"📁 Output: {api_dir}")
    print(f"🔧 Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ sphinx-apidoc completed successfully!")

        if result.stdout:
            print("📝 Output:")
            print(result.stdout)

    except subprocess.CalledProcessError as e:
        print("❌ sphinx-apidoc failed!")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        return False

    # Create a custom API index
    create_api_index(api_dir)

    return True


def create_api_index(api_dir):
    """Create a custom API index file."""

    api_index_content = """API Reference
=============

This section contains the complete API documentation for knitout-interpreter,
automatically generated from the source code docstrings.

.. note::
   This documentation is automatically generated from the source code.
   For the most up-to-date information, refer to the docstrings in the source code.

Complete Module Documentation
-----------------------------

.. toctree::
   :maxdepth: 2
   :caption: All Modules

   modules

Quick Reference
---------------

Main Package
~~~~~~~~~~~~

.. automodule:: knitout_interpreter
   :members: run_knitout, Knitout_Executer
   :noindex:

Core Classes
~~~~~~~~~~~~

.. autosummary::
   :nosignatures:

   knitout_interpreter.Knitout_Executer
   knitout_interpreter.knitout_language.Knitout_Parser
   knitout_interpreter.knitout_language.Knitout_Context
   knitout_interpreter.knitout_execution_structures.Carriage_Pass

Instruction Types
~~~~~~~~~~~~~~~~~

.. autosummary::
   :nosignatures:

   knitout_interpreter.knitout_operations.Knit_Instruction
   knitout_interpreter.knitout_operations.Tuck_Instruction
   knitout_interpreter.knitout_operations.Xfer_Instruction
   knitout_interpreter.knitout_operations.In_Instruction
   knitout_interpreter.knitout_operations.Out_Instruction

Search and Index
----------------

* :ref:`genindex` - Alphabetical index of all names
* :ref:`modindex` - Module index
* :ref:`search` - Search the documentation
"""

    index_file = api_dir / "index.rst"
    with open(index_file, "w", encoding="utf-8") as f:
        f.write(api_index_content)

    print(f"📖 Created custom API index: {index_file}")


def build_docs():
    """Build the complete documentation."""

    docs_dir = Path(__file__).parent
    source_dir = docs_dir / "source"
    build_dir = docs_dir / "build" / "html"

    cmd = [
        "poetry", "run", "sphinx-build",
        "-b", "html",  # Build HTML
        "-W",  # Treat warnings as errors
        str(source_dir),  # Source directory
        str(build_dir),  # Output directory
    ]

    print("\n🏗️  Building documentation...")
    print(f"🔧 Command: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Documentation built successfully!")
        print(f"📁 Output: {build_dir}")
        print(f"🌐 Open: {build_dir / 'index.html'}")

        if result.stdout:
            print("\n📝 Build output:")
            print(result.stdout)

        return True

    except subprocess.CalledProcessError as e:
        print("❌ Documentation build failed!")
        print(f"Exit code: {e.returncode}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        return False


def main():
    """Main function to generate and build documentation."""

    print("📚 Generating Sphinx API Documentation for knitout-interpreter")
    print("=" * 60)

    # Step 1: Generate API docs
    if not run_sphinx_apidoc():
        print("❌ Failed to generate API documentation")
        sys.exit(1)

    # Step 2: Build documentation (optional)
    print("\n" + "=" * 60)
    response = input("🤔 Would you like to build the documentation now? (y/N): ")

    if response.lower().startswith('y'):
        if build_docs():
            print("\n🎉 Documentation generation complete!")
            print("📖 Open docs/build/html/index.html to view the documentation")
        else:
            print("❌ Documentation build failed")
            sys.exit(1)
    else:
        print("\n✅ API documentation generated!")
        print("🏗️  Run 'poetry run sphinx-build -b html source build/html' to build")


if __name__ == "__main__":
    main()
