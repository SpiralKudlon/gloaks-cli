import pytest
from gloaks.core.scope import ScopeValidator

def test_scope_validation_allow_domain():
    validator = ScopeValidator()
    validator.scope_file = "TEST_MODE" # Simulate loaded scope
    validator.allowed_domains = ["example.com"]
    assert validator.is_target_allowed("example.com") is True
    assert validator.is_target_allowed("evil.com") is False

def test_scope_validation_wildcard():
    validator = ScopeValidator()
    validator.scope_file = "TEST_MODE"
    validator.allowed_domains = ["*.example.com"]
    assert validator.is_target_allowed("sub.example.com") is True

def test_scope_validation_wildcard_strict():
    validator = ScopeValidator()
    validator.scope_file = "TEST_MODE"
    validator.allowed_domains = ["*.example.com"]
    assert validator.is_target_allowed("example.com") is False

def test_scope_validation_exclusion():
    validator = ScopeValidator()
    validator.scope_file = "TEST_MODE"
    validator.allowed_domains = ["*.example.com"]
    validator.excluded_domains = ["secret.example.com"]
    
    # Logic check: exclusion takes precedence
    assert validator.is_target_allowed("secret.example.com") is False
    assert validator.is_target_allowed("public.example.com") is True
