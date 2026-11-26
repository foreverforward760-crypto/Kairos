import pytest
from fastapi import HTTPException
from starlette.requests import Request

import api_kairos as api


def make_request(host: str) -> Request:
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": "/protected",
        "raw_path": b"/protected",
        "query_string": b"",
        "headers": [],
        "client": (host, 12345),
        "server": ("localhost", 8002),
    }
    return Request(scope)


def test_api_key_required_when_not_in_local_dev_mode(monkeypatch):
    monkeypatch.setattr(api, "KAIROS_API_KEY", None)
    monkeypatch.setattr(api, "KAIROS_ALLOW_INSECURE_LOCAL", False)
    with pytest.raises(HTTPException) as exc:
        api.require_api_key(make_request("127.0.0.1"), None)
    assert exc.value.status_code == 503


def test_loopback_dev_mode_requires_explicit_opt_in(monkeypatch):
    monkeypatch.setattr(api, "KAIROS_API_KEY", None)
    monkeypatch.setattr(api, "KAIROS_ALLOW_INSECURE_LOCAL", True)
    assert api.require_api_key(make_request("127.0.0.1"), None) is None


def test_loopback_dev_mode_does_not_allow_remote_clients(monkeypatch):
    monkeypatch.setattr(api, "KAIROS_API_KEY", None)
    monkeypatch.setattr(api, "KAIROS_ALLOW_INSECURE_LOCAL", True)
    with pytest.raises(HTTPException) as exc:
        api.require_api_key(make_request("203.0.113.10"), None)
    assert exc.value.status_code == 503


def test_valid_api_key(monkeypatch):
    monkeypatch.setattr(api, "KAIROS_API_KEY", "test-secret-key")
    monkeypatch.setattr(api, "KAIROS_ALLOW_INSECURE_LOCAL", False)
    assert api.require_api_key(make_request("203.0.113.10"), "test-secret-key") is None


def test_invalid_api_key(monkeypatch):
    monkeypatch.setattr(api, "KAIROS_API_KEY", "test-secret-key")
    monkeypatch.setattr(api, "KAIROS_ALLOW_INSECURE_LOCAL", False)
    with pytest.raises(HTTPException) as exc:
        api.require_api_key(make_request("203.0.113.10"), "wrong-key")
    assert exc.value.status_code == 401


def test_request_models_bound_input_sizes():
    with pytest.raises(Exception):
        api.KairosInput(system_id="x", nsdt=[1.0, 2.0])
    with pytest.raises(Exception):
        api.ReadingInput(stage=1, canonical_name="SPARK", text="x" * 10001)
