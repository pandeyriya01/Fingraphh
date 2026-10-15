"""
End-to-End Test Suite for Complete FinGraph Pipeline
"""

import pytest
from scripts.run_e2e_pipeline import run_end_to_end_pipeline

def test_full_pipeline_execution():
    success = run_end_to_end_pipeline()
    assert success is True
