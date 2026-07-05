"""Test configuration for Vector Database Agent."""

import pytest


@pytest.fixture
def agent_config():
    return {"name": "vector-database-agent", "category": "AI Engineering"}
