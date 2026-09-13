import pytest
from src.config import settings

def test_config_loaded():
    assert settings.llm_model is not None

def test_imports():
    import src.pipeline
    import src.classifier
    import src.triage
    assert True
