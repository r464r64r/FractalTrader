"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import fixtures from sample_data
from tests.fixtures.sample_data import *  # noqa: F401, F403
