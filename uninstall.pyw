import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

_ROOT       = Path(__file__).parent
_CONFIG_DIR = Path.home() / ".config" / "doctomd"
_PACKAGES   = [
    "PyQt6", "PyQt6-Qt6", "PyQt6-sip",
    "PyQt6-WebEngine", "PyQt6-WebEngine-Qt6", "PyQt6-WebEngine-Qt6-sip",
    "markitdown", "markdown-it-py", "mdurl", "linkify-it-py",
    "docling", "docling-core", "docling-ibm-models", "docling-parse",
    "torch", "torchvision", "torchaudio",
]


def _run(root: tk.Tk) -> None:
    root.title("DocToMD — Desinstalador")
    root.resizable(False, False)
    root.geometry("420x200")
    root.configure(bg="#0f172a")

    tk.Label(
        root, text="DocToMD — Desinstalador",
        bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 12, "bold"),
    ).pack(pady=(20, 4))

    status = tk.StringVar(value="Listo para desinstalar.")
    tk.Label(root, textvariable=status, bg="#0f172a", fg="#94a3b8",
             font=("Segoe UI", 10), wraplength=380).pack(pady=4)

    bar = ttk.Progressbar(root, mode="indeterminate", length=360)
    bar.pack(pady=8)

    def _do_uninstall():
        btn.config(state="disabled")
        bar.start(10)

        status.set("Desinstalando paquetes…")
        root.update()
        subprocess.run(
            [sys.executable, "-m", "pip", "uninstall", "-y"] + _PACKAGES,
            capture_output=True,
        )

        status.set("Eliminando perfil de hardware…")
        root.update()
        if _CONFIG_DIR.exists():
            shutil.rmtree(_CONFIG_DIR, ignore_errors=True)

        status.set("Eliminando archivos temporales…")
        root.update()
        for leftover in [_ROOT / "detector" / "build", _ROOT / "requirements"]:
            if leftover.exists():
                shutil.rmtree(leftover, ignore_errors=True)

        bar.stop()
        status.set("Desinstalación completada.")
        btn.config(text="Cerrar", state="normal", command=root.destroy,
                   bg="#1e293b", fg="#94a3b8", activebackground="#334155")
        root.update()

    confirmed = messagebox.askyesno(
        "Desinstalar DocToMD",
        "Esto eliminará:\n\n"
        "  • PyQt6, markitdown, docling, torch y sus dependencias\n"
        "  • El perfil de hardware (~/.config/doctomd/)\n"
        "  • Archivos temporales del detector\n\n"
        "¿Continuar?",
    )
    if not confirmed:
        root.destroy()
        return

    btn = tk.Button(
        root, text="Desinstalando…", state="disabled",
        bg="#ef4444", fg="white", font=("Segoe UI", 10),
        relief="flat", padx=16, pady=6,
    )
    btn.pack(pady=4)
    root.after(100, _do_uninstall)


root = tk.Tk()
_run(root)
root.mainloop()
