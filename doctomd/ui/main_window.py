import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QMainWindow, QPushButton,
    QSplitter, QStatusBar, QVBoxLayout, QWidget,
)
from PyQt6.QtCore import Qt

from doctomd.ui.widgets.engine_toggle import EngineToggle
from doctomd.ui.widgets.file_drop import FileDropWidget
from doctomd.ui.widgets.markdown_view import MarkdownView

_MAIN_STYLE = """
QMainWindow, QWidget { background: #0f172a; color: #e2e8f0; }
QStatusBar { background: #1e293b; color: #64748b; font-size: 11px; }
QSplitter::handle { background: #334155; width: 1px; }
"""
_HEADER_STYLE = "background:#1e293b; border-bottom:1px solid #334155;"
_TITLE_STYLE  = "color:#e2e8f0; font-size:16px; font-weight:600;"
_BTN_CONVERT  = (
    "QPushButton { background:#3b82f6; color:white; border:none; border-radius:6px;"
    " padding:10px; font-size:14px; font-weight:500; }"
    "QPushButton:disabled { background:#1e3a5f; color:#475569; }"
    "QPushButton:hover:!disabled { background:#2563eb; }"
)
_ERROR_STYLE  = "color:#f87171; font-size:13px;"


# ── async conversion worker ───────────────────────────────────────────────

class _ConversionSignals(QObject):
    finished = pyqtSignal(str)
    error    = pyqtSignal(str)


class _ConversionTask(QRunnable):
    def __init__(self, file_path: Path, engine: str):
        super().__init__()
        self.signals  = _ConversionSignals()
        self._path    = file_path
        self._engine  = engine

    def run(self):
        try:
            if self._engine == "markitdown":
                from doctomd.converters import markitdown
                result = markitdown.convert(self._path)
            else:
                from doctomd.converters import docling
                result = docling.convert(self._path)
            self.signals.finished.emit(result)
        except Exception as exc:
            self.signals.error.emit(str(exc))


# ── main window ───────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocToMD")
        self.setMinimumSize(900, 600)
        self.resize(1200, 700)
        self.setStyleSheet(_MAIN_STYLE)

        self._current_file: Path | None = None
        self._engine = "markitdown"

        self._build_ui()

    def _build_ui(self):
        # ── header ────────────────────────────────────────────────────────
        header = QWidget()
        header.setStyleSheet(_HEADER_STYLE)
        header.setFixedHeight(52)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(20, 0, 20, 0)

        title = QLabel("DocToMD")
        title.setStyleSheet(_TITLE_STYLE)
        h_layout.addWidget(title)
        h_layout.addStretch()

        # ── left panel ────────────────────────────────────────────────────
        left_panel = QWidget()
        left_panel.setMinimumWidth(280)
        left_panel.setMaximumWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(20, 20, 20, 20)
        left_layout.setSpacing(14)

        self._file_drop = FileDropWidget()
        self._file_drop.file_selected.connect(self._on_file_selected)

        self._file_info = QLabel("")
        self._file_info.setStyleSheet("color:#94a3b8; font-size:13px;")
        self._file_info.setVisible(False)

        self._engine_toggle = EngineToggle()
        self._engine_toggle.engine_changed.connect(self._on_engine_changed)

        self._btn_convert = QPushButton("Convertir")
        self._btn_convert.setStyleSheet(_BTN_CONVERT)
        self._btn_convert.setEnabled(False)
        self._btn_convert.clicked.connect(self._on_convert)

        self._error_label = QLabel("")
        self._error_label.setStyleSheet(_ERROR_STYLE)
        self._error_label.setWordWrap(True)
        self._error_label.setVisible(False)

        left_layout.addWidget(self._file_drop)
        left_layout.addWidget(self._file_info)
        left_layout.addWidget(self._engine_toggle)
        left_layout.addWidget(self._btn_convert)
        left_layout.addWidget(self._error_label)
        left_layout.addStretch()

        # ── right panel ───────────────────────────────────────────────────
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(20, 20, 20, 20)

        self._markdown_view = MarkdownView()
        right_layout.addWidget(self._markdown_view)

        # ── splitter ──────────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # ── root widget ───────────────────────────────────────────────────
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_layout.addWidget(header)
        root_layout.addWidget(splitter)

        self.setCentralWidget(root)
        self.setStatusBar(QStatusBar())

    # ── slots ─────────────────────────────────────────────────────────────

    def _on_file_selected(self, path: Path):
        self._current_file = path
        self._btn_convert.setEnabled(True)
        self._error_label.setVisible(False)
        self._markdown_view.set_markdown(None)
        size_mb = path.stat().st_size / (1024 * 1024)
        self._file_info.setText(f"{path.name}  ·  {size_mb:.1f} MB")
        self._file_info.setVisible(True)
        self.statusBar().showMessage(f"Archivo listo: {path.name}")

    def _on_engine_changed(self, engine: str):
        self._engine = engine
        self.statusBar().showMessage(f"Motor: {engine}")

    def _on_convert(self):
        if not self._current_file:
            return
        self._btn_convert.setEnabled(False)
        self._error_label.setVisible(False)
        self._markdown_view.set_loading(True)
        self.statusBar().showMessage("Convirtiendo…")

        task = _ConversionTask(self._current_file, self._engine)
        task.signals.finished.connect(self._on_conversion_done)
        task.signals.error.connect(self._on_conversion_error)
        QThreadPool.globalInstance().start(task)

    def _on_conversion_done(self, markdown: str):
        self._markdown_view.set_loading(False)
        self._markdown_view.set_markdown(markdown)
        self._btn_convert.setEnabled(True)
        self.statusBar().showMessage("Conversión completada.")

    def _on_conversion_error(self, error_msg: str):
        self._markdown_view.set_loading(False)
        self._btn_convert.setEnabled(True)
        self._error_label.setText(f"Error: {error_msg}")
        self._error_label.setVisible(True)
        self.statusBar().showMessage("Error en la conversión.")
