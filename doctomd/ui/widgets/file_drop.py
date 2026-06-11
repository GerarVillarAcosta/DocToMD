from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

ACCEPTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".png", ".jpg", ".jpeg", ".webp"}

_STYLE_IDLE = """
    QWidget#DropZone {
        border: 2px dashed #334155;
        border-radius: 8px;
        background: #0f172a;
    }
"""
_STYLE_HOVER = """
    QWidget#DropZone {
        border: 2px dashed #3b82f6;
        border-radius: 8px;
        background: #0f172a;
    }
"""
_STYLE_HAS_FILE = """
    QWidget#DropZone {
        border: 2px solid #3b82f6;
        border-radius: 8px;
        background: #0f172a;
    }
"""


class FileDropWidget(QWidget):
    file_selected = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._current_file: Path | None = None

        self._icon_label = QLabel("⬆", self)
        self._icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon_label.setStyleSheet("color:#64748b; font-size:28px; border:none;")

        self._text_label = QLabel("Arrastra o selecciona un archivo", self)
        self._text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._text_label.setStyleSheet("color:#64748b; font-size:13px; border:none;")

        self._hint_label = QLabel("PDF · DOCX · PPTX · XLSX · Imágenes", self)
        self._hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hint_label.setStyleSheet("color:#475569; font-size:11px; border:none;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setSpacing(6)
        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)
        layout.addWidget(self._hint_label)

        self.setStyleSheet(_STYLE_IDLE)
        self.setMinimumHeight(120)

    # ── drag events ───────────────────────────────────────────────────────

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(_STYLE_HOVER)

    def dragLeaveEvent(self, event):
        self.setStyleSheet(_STYLE_HAS_FILE if self._current_file else _STYLE_IDLE)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            if path.suffix.lower() in ACCEPTED_EXTENSIONS:
                self._accept_file(path)
                return
        self.setStyleSheet(_STYLE_HAS_FILE if self._current_file else _STYLE_IDLE)

    # ── click to open dialog ──────────────────────────────────────────────

    def mousePressEvent(self, event):
        from PyQt6.QtWidgets import QFileDialog
        extensions = " ".join(f"*{e}" for e in sorted(ACCEPTED_EXTENSIONS))
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo",
            "",
            f"Documentos soportados ({extensions})",
        )
        if path:
            self._accept_file(Path(path))

    # ── internal ──────────────────────────────────────────────────────────

    def _accept_file(self, path: Path):
        self._current_file = path
        self._text_label.setText(path.name)
        size_mb = path.stat().st_size / (1024 * 1024)
        self._hint_label.setText(f"{size_mb:.1f} MB · Haz clic para cambiar")
        self._icon_label.setText("📄")
        self.setStyleSheet(_STYLE_HAS_FILE)
        self.file_selected.emit(path)

    def clear(self):
        self._current_file = None
        self._icon_label.setText("⬆")
        self._text_label.setText("Arrastra o selecciona un archivo")
        self._hint_label.setText("PDF · DOCX · PPTX · XLSX · Imágenes")
        self.setStyleSheet(_STYLE_IDLE)
