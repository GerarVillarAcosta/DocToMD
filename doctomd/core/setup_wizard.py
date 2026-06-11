"""
setup_wizard.py — First-run hardware detection and dependency installer.

Flow:
  1. If ~/.config/doctomd/hardware.json exists → skip (already configured).
  2. Try to compile detector/detect.c and run the resulting binary to get JSON.
  3. If compilation fails → fall back to pure-Python detection.
  4. Save profile to ~/.config/doctomd/hardware.json.
  5. pip install requirements/base.txt (always).
  6. pip install requirements/{cuda|rocm|cpu}.txt (according to detected GPU).
  7. Delete requirements/ folder — no longer needed once installed.
  8. Delete detector/build/ — binary served its purpose.
"""

import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from doctomd.core.hardware import hardware_profile_exists, save_hardware

_REPO_ROOT        = Path(__file__).resolve().parents[2]
_REQUIREMENTS_DIR = _REPO_ROOT / "requirements"
_DETECTOR_SRC     = _REPO_ROOT / "detector" / "detect.c"
_DETECTOR_BUILD   = _REPO_ROOT / "detector" / "build"
_DETECTOR_BIN     = _DETECTOR_BUILD / (
    "detect.exe" if platform.system() == "Windows" else "detect"
)


# ── compile the C detector ────────────────────────────────────────────────

def _try_compile() -> bool:
    """Try to compile detect.c with cmake or gcc. Returns True on success."""
    _DETECTOR_BUILD.mkdir(exist_ok=True)

    if shutil.which("cmake"):
        r1 = subprocess.run(
            ["cmake", str(_DETECTOR_SRC.parent), "-B", str(_DETECTOR_BUILD)],
            capture_output=True,
        )
        if r1.returncode == 0:
            r2 = subprocess.run(
                ["cmake", "--build", str(_DETECTOR_BUILD), "--config", "Release"],
                capture_output=True,
            )
            if r2.returncode == 0:
                release_bin = _DETECTOR_BUILD / "Release" / _DETECTOR_BIN.name
                if release_bin.exists() and not _DETECTOR_BIN.exists():
                    release_bin.rename(_DETECTOR_BIN)
                return _DETECTOR_BIN.exists()

    if shutil.which("gcc"):
        r = subprocess.run(
            ["gcc", "-O2", "-o", str(_DETECTOR_BIN), str(_DETECTOR_SRC)],
            capture_output=True,
        )
        return r.returncode == 0

    if shutil.which("cl"):
        r = subprocess.run(
            ["cl", str(_DETECTOR_SRC), f"/Fe{_DETECTOR_BIN}"],
            capture_output=True,
        )
        return r.returncode == 0

    return False


# ── pure-Python fallback detection ───────────────────────────────────────

def _py_detect() -> dict:
    """Detect hardware without the C binary."""
    import re

    profile: dict = {
        "gpu": "none",
        "cuda_version": "n/a",
        "driver_version": "n/a",
        "vram_mb": 0,
        "ram_mb": 0,
        "cpu_vendor": "unknown",
    }

    if platform.system() == "Linux":
        try:
            mem = Path("/proc/meminfo").read_text()
            m = re.search(r"MemTotal:\s+(\d+)", mem)
            if m:
                profile["ram_mb"] = int(m.group(1)) // 1024
        except OSError:
            pass
    elif platform.system() == "Windows":
        try:
            import ctypes
            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength",                ctypes.c_ulong),
                    ("dwMemoryLoad",             ctypes.c_ulong),
                    ("ullTotalPhys",             ctypes.c_ulonglong),
                    ("ullAvailPhys",             ctypes.c_ulonglong),
                    ("ullTotalPageFile",         ctypes.c_ulonglong),
                    ("ullAvailPageFile",         ctypes.c_ulonglong),
                    ("ullTotalVirtual",          ctypes.c_ulonglong),
                    ("ullAvailVirtual",          ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual",  ctypes.c_ulonglong),
                ]
            ms = MEMORYSTATUSEX()
            ms.dwLength = ctypes.sizeof(ms)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
            profile["ram_mb"] = ms.ullTotalPhys // (1024 * 1024)
        except Exception:
            pass

    if platform.system() == "Linux":
        try:
            cpuinfo = Path("/proc/cpuinfo").read_text()
            m = re.search(r"vendor_id\s*:\s*(\S+)", cpuinfo)
            if m:
                v = m.group(1)
                profile["cpu_vendor"] = "Intel" if "Intel" in v else ("AMD" if "AMD" in v else v)
        except OSError:
            pass
    else:
        import platform as _p
        proc = _p.processor()
        if "Intel" in proc:
            profile["cpu_vendor"] = "Intel"
        elif "AMD" in proc:
            profile["cpu_vendor"] = "AMD"

    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=driver_version,memory.total",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0 and r.stdout.strip():
            parts = [p.strip() for p in r.stdout.strip().split(",")]
            profile["gpu"] = "nvidia"
            profile["driver_version"] = parts[0] if parts else "unknown"
            profile["vram_mb"] = int(parts[1]) if len(parts) > 1 else 0
            r2 = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=10)
            m = re.search(r"CUDA Version:\s*([\d.]+)", r2.stdout)
            if m:
                profile["cuda_version"] = m.group(1)
            return profile
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass

    try:
        r = subprocess.run(
            ["rocm-smi", "--showproductname"],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            profile["gpu"] = "amd"
            return profile
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return profile


# ── run the C binary ──────────────────────────────────────────────────────

def _run_detector() -> dict | None:
    if not _DETECTOR_BIN.exists():
        return None
    try:
        r = subprocess.run(
            [str(_DETECTOR_BIN)], capture_output=True, text=True, timeout=15
        )
        if r.returncode == 0:
            return json.loads(r.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        pass
    return None


# ── pip install ───────────────────────────────────────────────────────────

def _pip_install(req_file: Path) -> None:
    if not req_file.exists():
        return
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"],
        check=False,
    )


def _install_all(gpu: str) -> None:
    """Install base requirements, then the GPU-specific ones."""
    _pip_install(_REQUIREMENTS_DIR / "base.txt")

    gpu_file_map = {
        "nvidia": _REQUIREMENTS_DIR / "cuda.txt",
        "amd":    _REQUIREMENTS_DIR / "rocm.txt",
    }
    _pip_install(gpu_file_map.get(gpu, _REQUIREMENTS_DIR / "cpu.txt"))


# ── post-install cleanup ──────────────────────────────────────────────────

def _cleanup() -> None:
    """Remove requirements folder and detector build dir after use."""
    if _REQUIREMENTS_DIR.exists():
        shutil.rmtree(_REQUIREMENTS_DIR, ignore_errors=True)

    if _DETECTOR_BUILD.exists():
        shutil.rmtree(_DETECTOR_BUILD, ignore_errors=True)


# ── public entry point ────────────────────────────────────────────────────

def run_if_needed(progress_callback=None) -> dict:
    """
    Run first-time setup if hardware profile doesn't exist.
    Returns the hardware profile dict.
    progress_callback(message: str) is called with status updates if provided.
    """
    def _msg(m: str):
        if progress_callback:
            progress_callback(m)

    if hardware_profile_exists():
        from doctomd.core.hardware import get_hardware
        return get_hardware()

    _msg("Detectando hardware…")

    if not _DETECTOR_BIN.exists():
        _msg("Compilando detector de hardware…")
        _try_compile()

    profile = _run_detector()

    if profile is None:
        _msg("Usando detección Python (sin binario C)…")
        profile = _py_detect()

    _msg(
        f"Hardware detectado: GPU={profile.get('gpu', 'none')}, "
        f"RAM={profile.get('ram_mb', 0)} MB"
    )
    save_hardware(profile)

    _msg("Instalando dependencias base…")
    _msg("Instalando dependencias para tu hardware…")
    _install_all(profile.get("gpu", "none"))

    _msg("Limpiando archivos de instalación…")
    _cleanup()

    _msg("Configuración inicial completada.")
    return profile
