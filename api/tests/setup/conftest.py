"""
Fixtures para tests setup FASE 0.
"""
import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Path raiz proyecto."""
    return Path("/tmp/iact-project")


@pytest.fixture
def callcentersite_path(project_root):
    """Path callcentersite/."""
    return project_root / "callcentersite"
