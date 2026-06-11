import json
from pathlib import Path

_CONFIG_PATH = Path.home() / ".config" / "doctomd" / "hardware.json"


def get_hardware() -> dict:
    """Return the cached hardware profile, or empty dict if not yet detected."""
    if _CONFIG_PATH.exists():
        try:
            return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def hardware_profile_exists() -> bool:
    return _CONFIG_PATH.exists()


def save_hardware(profile: dict) -> None:
    _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _CONFIG_PATH.write_text(
        json.dumps(profile, indent=2), encoding="utf-8"
    )
