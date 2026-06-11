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
        monkeypatch.setattr(wiz_mod, "_install_all", lambda _: None)
        monkeypatch.setattr(wiz_mod, "_cleanup", lambda: None)

        result = wiz_mod.run_if_needed()
        assert result["gpu"] == "none"

    def test_install_all_calls_base_then_cuda(self, monkeypatch, tmp_path):
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        (req_dir / "base.txt").write_text("PyQt6\n")
        (req_dir / "cuda.txt").write_text("torch\n")
        monkeypatch.setattr(wiz_mod, "_REQUIREMENTS_DIR", req_dir)

        installed = []
        monkeypatch.setattr(
            subprocess, "run",
            lambda args, **kw: installed.append(args) or MagicMock(returncode=0),
        )
        wiz_mod._install_all("nvidia")

        assert len(installed) == 2
        assert any("base.txt" in str(a) for a in installed[0])
        assert any("cuda.txt" in str(a) for a in installed[1])

    def test_install_all_falls_back_to_cpu(self, monkeypatch, tmp_path):
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        (req_dir / "base.txt").write_text("PyQt6\n")
        (req_dir / "cpu.txt").write_text("torch\n")
        monkeypatch.setattr(wiz_mod, "_REQUIREMENTS_DIR", req_dir)

        installed = []
        monkeypatch.setattr(
            subprocess, "run",
            lambda args, **kw: installed.append(args) or MagicMock(returncode=0),
        )
        wiz_mod._install_all("none")

        assert len(installed) == 2
        assert any("cpu.txt" in str(a) for a in installed[1])

    def test_install_all_skips_missing_gpu_file(self, monkeypatch, tmp_path):
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        (req_dir / "base.txt").write_text("PyQt6\n")
        # No rocm.txt
        monkeypatch.setattr(wiz_mod, "_REQUIREMENTS_DIR", req_dir)

        installed = []
        monkeypatch.setattr(
            subprocess, "run",
            lambda args, **kw: installed.append(args) or MagicMock(returncode=0),
        )
        wiz_mod._install_all("amd")
        # Only base.txt is installed; rocm.txt missing → skipped
        assert len(installed) == 1
        assert any("base.txt" in str(a) for a in installed[0])

    def test_cleanup_removes_requirements_and_build(self, tmp_path, monkeypatch):
        req_dir = tmp_path / "requirements"
        req_dir.mkdir()
        (req_dir / "base.txt").write_text("x")

        build_dir = tmp_path / "detector" / "build"
        build_dir.mkdir(parents=True)
        (build_dir / "detect.exe").write_text("binary")

        monkeypatch.setattr(wiz_mod, "_REQUIREMENTS_DIR", req_dir)
        monkeypatch.setattr(wiz_mod, "_DETECTOR_BUILD", build_dir)

        wiz_mod._cleanup()

        assert not req_dir.exists()
        assert not build_dir.exists()
