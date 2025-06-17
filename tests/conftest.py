"""Pytest configuration for cisco.radkit collection tests."""

import os
import sys
from pathlib import Path

# Add the collection root to Python path so imports work
collection_root = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(collection_root))

# Create ansible_collections namespace module structure for pytest
ansible_collections_path = collection_root / "ansible_collections"
cisco_path = ansible_collections_path / "cisco"
radkit_path = cisco_path / "radkit"

# Create directories if they don't exist
ansible_collections_path.mkdir(exist_ok=True)
cisco_path.mkdir(exist_ok=True)
radkit_path.mkdir(exist_ok=True)

# Create __init__.py files to make them proper Python packages
for path in [ansible_collections_path, cisco_path, radkit_path]:
    init_file = path / "__init__.py"
    if not init_file.exists():
        init_file.write_text('"""Namespace package for testing."""\n')

# Create symlinks to the actual plugin directories
plugins_src = collection_root / "plugins"
plugins_dst = radkit_path / "plugins"

if not plugins_dst.exists():
    try:
        # Try to create a symlink first
        plugins_dst.symlink_to(plugins_src)
    except (OSError, NotImplementedError):
        # If symlinks don't work (Windows), copy the structure
        import shutil
        shutil.copytree(plugins_src, plugins_dst, dirs_exist_ok=True)

# Add the ansible_collections path to Python path
sys.path.insert(0, str(collection_root))
