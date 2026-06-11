"""
Tests for doctomd.core — hardware profile and setup wizard.
No real hardware access; everything is mocked or uses temp dirs.
"""

import json
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import doctomd.core.hardware as hw_mod
import doctomd.core.setup_wizard as wiz_mod


# ── hardware.py ───────────────────────────────────────────────────────────

class TestHardware:
    def test_get_hardware_returns_empty_when_no_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hw_mod, "_CONFIG_PATH", tmp_path / "hardware.json")
        assert hw_mod.get_hardware() == {}

    def test_get_hardware_returns_profile(self, tmp_path, monkeypatch):
        config = tmp_path / "hardware.json"
        profile = {"gpu": "nvidia", "cuda_version": "12.4", "ram_mb": 16384}
        config.write_text(json.dumps(profile))
        monkeypatch.setattr(hw_mod, "_CONFIG_PATH", config)
        assert hw_mod.get_hardware() == profile

    def test_get_hardware_returns_empty_on_bad_json(self, tmp_path, monkeypatch):
        config = tmp_path / "hardware.json"
        config.write_text("not-json{{{")
        monkeypatch.setattr(hw_mod, "_CONFIG_PATH", config)
        assert hw_mod.get_hardware() == {}

    def test_hardware_profile_exists_false(self, tmp_path, monkeypatch):
        monkeypatch.setattr(hw_mod, "_CONFIG_PATH", tmp_path / "hardware.json")
        assert not hw_mod.hardware_profile_exists()

    def test_hardware_profile_exists_true(self, tmp_path, monkeypatch):
        config = tmp_path / "hardware.json"
        config.write_text("{}")
        monkeypatch.setattr(hw_mod, "_CONFIG_PATH", config)
        assert hw_mod.hardware_profile_exists()

    def test_save_hardware_creates_file_and_parent_dirs(self, tmp_path, monkeypatch):
        config = tmp_path / "subdir" / "hardware.json"
        monkeypatch.setattr(hw_mod, "_CONFIG_PATH", config)
        hw_mod.save_hardware({"gpu": "none", "ram_mb": 8192})
        assert config.exists()
        assert json.loads(config.read_text())["gpu"] == "none"


# ── setup_wizard.py ───────────────────────────────────────────────────────

class TestSetupWizard:
    def test_run_if_needed_skips_when_profile_exists(self, monkeypatch):
        fake_profile = {"gpu": "nvidia", "cuda_version": "12.4"}
        monkeypatch.setattr(wiz_mod, "hardware_profile_exists", lambda: True)
        # patch get_hardware at the source module
        monkeypatch.setattr(hw_mod, "get_hardware", lambda: fake_profile)
        result = wiz_mod.run_if_needed()
        assert result == fake_profile

    def test_run_if_needed_uses_py_fallback_when_no_binary(self, monkeypatch, tmp_path):
        fake_profile = {
            "gpu": "none", "ram_mb": 8192, "cpu_vendor": "Intel",
            "cuda_version": "n/a", "driver_version": "n/a", "vram_mb": 0,
        }
        monkeypatch.setattr(wiz_mod, "hardware_profile_exists", lambda: False)
        monkeypatch.setattr(wiz_mod, "_DETECTOR_BIN", tmp_path / "detect_nonexistent")
        monkeypatch.setattr(wiz_mod, "_try_compile", lambda: False)
        monkeypatch.setattr(wiz_mod, "_py_detect", lambda: fake_profile)
        monkeypatch.setattr(wiz_mod, "save_hardware", lambda _: None)
        monkeypatch.setattr(wiz_mod, "_install_requirements", lambda _: None)

        result = wiz_mod.run_if_needed()
        assert result["gpu"] == "none"

    def test_install_requirements_cuda(self, monkeypatch, tmp_path):
        req_file = tmp_path / "requirements-cuda.txt"
        req_file.write_text("torch\n")
        monkeypatch.setattr(wiz_mod, "_REPO_ROOT", tmp_path)

        called_args = []
        monkeypatch.setattr(
            subprocess, "run",
            lambda args, **kw: called_args.append(args) or MagicMock(returncode=0),
        )
        wiz_mod._install_requirements("nvidia")
        assert called_args, "subprocess.run was not called"
        assert any("requirements-cuda.txt" in str(a) for a in called_args[0])

    def test_install_requirements_falls_back_to_cpu(self, monkeypatch, tmp_path):
        req_cpu = tmp_path / "requirements-cpu.txt"
        req_cpu.write_text("torch\n")
        monkeypatch.setattr(wiz_mod, "_REPO_ROOT", tmp_path)

        called_args = []
        monkeypatch.setattr(
            subprocess, "run",
            lambda args, **kw: called_args.append(args) or MagicMock(returncode=0),
        )
        wiz_mod._install_requirements("none")
        assert called_args
        assert any("requirements-cpu.txt" in str(a) for a in called_args[0])

    def test_install_requirements_skips_missing_file(self, monkeypatch, tmp_path):
        # No requirements-rocm.txt → should not call pip
        monkeypatch.setattr(wiz_mod, "_REPO_ROOT", tmp_path)
        called = []
        monkeypatch.setattr(
            subprocess, "run",
            lambda args, **kw: called.append(args),
        )
        wiz_mod._install_requirements("amd")
        assert called == []
