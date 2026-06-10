import asyncio
from unittest.mock import patch

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_convert_unsupported_format():
    response = client.post(
        "/api/v1/convert",
        data={"engine": "markitdown"},
        files={"file": ("test.xyz", b"content", "application/octet-stream")},
    )
    assert response.status_code == 400
    assert "Unsupported format" in response.json()["detail"]


def test_convert_unknown_engine():
    response = client.post(
        "/api/v1/convert",
        data={"engine": "unknown"},
        files={"file": ("test.pdf", b"%PDF content", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Unknown engine" in response.json()["detail"]


def test_convert_success_with_markitdown():
    with patch("backend.api.routes.markitdown.convert", return_value="# Test"):
        response = client.post(
            "/api/v1/convert",
            data={"engine": "markitdown"},
            files={"file": ("test.pdf", b"%PDF content", "application/pdf")},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["markdown"] == "# Test"
    assert data["engine"] == "markitdown"
    assert data["filename"] == "test.pdf"


def test_convert_engine_failure_returns_422():
    with patch("backend.api.routes.markitdown.convert", side_effect=Exception("parse error")):
        response = client.post(
            "/api/v1/convert",
            data={"engine": "markitdown"},
            files={"file": ("test.pdf", b"%PDF content", "application/pdf")},
        )
    assert response.status_code == 422
    assert "parse error" in response.json()["detail"]


def test_convert_timeout_returns_504():
    with patch("backend.api.routes.asyncio.wait_for", side_effect=asyncio.TimeoutError()):
        response = client.post(
            "/api/v1/convert",
            data={"engine": "markitdown"},
            files={"file": ("test.pdf", b"%PDF content", "application/pdf")},
        )
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"]
