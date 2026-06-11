import platform
import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent

try:
    import PyQt6
except ImportError:
    req = _ROOT / "requirements" / "base.txt"
    if req.exists():
        if platform.system() == "Windows":
            subprocess.run(
                ["cmd", "/c", f"pip install -r \"{req}\" && echo. && echo Listo. && timeout /t 2"],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req)])

from doctomd.main import main
main()
