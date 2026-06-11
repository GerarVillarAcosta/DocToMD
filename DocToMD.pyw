import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent

try:
    import PyQt6
except ImportError:
    req = _ROOT / "requirements" / "base.txt"
    if req.exists():
        subprocess.run(
            ["cmd", "/c", f"pip install -r \"{req}\" && echo. && echo Listo. && timeout /t 2"],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )

from doctomd.main import main
main()
