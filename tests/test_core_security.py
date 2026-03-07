"""Tests for app.core.security (password hashing and token hashing)."""

import pytest
from app.core.security import hash_password, verify_password, hash_token


def test_hash_password_returns_string():
    h = hash_password("mypassword")
    assert isinstance(h, str)
    assert h != "mypassword"


def test_verify_password_correct():
    h = hash_password("secret")
    assert verify_password("secret", h) is True


def test_verify_password_incorrect():
    h = hash_password("secret")
    assert verify_password("wrong", h) is False


def test_hash_token_deterministic():
    t = "some-jwt-token"
    assert hash_token(t) == hash_token(t)


def test_hash_token_returns_hex_string():
    h = hash_token("token")
    assert isinstance(h, str)
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)
