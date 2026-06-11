"""
DocToMD — native desktop entry point.

Usage:
    python -m doctomd
    # or via pyproject.toml script entry point: doctomd
"""

import sys

from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QProgressBar, QVBoxLayout


# ── first-run setup dialog ────────────────────────────────────────────────

class _SetupDialog(QDialog):
    """Non-blocking setup splash shown while setup_wizard runs."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocToMD — Configuración inicial")
        self.setFixedSize(380, 140)
        self.setStyleSheet("background:#0f172a; color:#e2e8f0;")

        self._label = QLabel("Iniciando configuración…")
        self._label.setStyleSheet("color:#94a3b8; font-size:13px;")

        bar = QProgressBar()
        bar.setRange(0, 0)  # indeterminate
        bar.setStyleSheet(
            "QProgressBar { border:none; background:#1e293b; border-radius:4px; height:6px; }"
            "QProgressBar::chunk { background:#3b82f6; border-radius:4px; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(QLabel("DocToMD").setObjectName if False else QLabel("DocToMD"))
        layout.addWidget(self._label)
        layout.addWidget(bar)

    def update_message(self, msg: str):
        self._label.setText(msg)
        QApplication.processEvents()


# ── main ──────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DocToMD")
    app.setOrganizationName("GerarVillarAcosta")

    from doctomd.core.hardware import hardware_profile_exists

    if not hardware_profile_exists():
        dialog = _SetupDialog()
        dialog.show()
        QApplication.processEvents()

        from doctomd.core.setup_wizard import run_if_needed
        run_if_needed(progress_callback=dialog.update_message)

        dialog.close()

    from doctomd.ui.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
