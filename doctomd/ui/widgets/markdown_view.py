from PyQt6.QtCore import QUrl, pyqtSignal
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    _HAS_WEBENGINE = True
except ImportError:
    _HAS_WEBENGINE = False

_PREVIEW_CSS = """
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  font-size: 14px; line-height: 1.7; color: #111;
  max-width: 860px; margin: 0 auto; padding: 24px;
}
h1,h2,h3,h4 { margin: 1em 0 .4em; }
p { margin-bottom: .9em; }
ul,ol { padding-left: 1.5em; margin-bottom: .9em; }
code { background:#f1f5f9; padding:2px 5px; border-radius:3px; font-size:.9em; }
pre  { background:#f1f5f9; padding:14px; border-radius:6px; overflow-x:auto; margin-bottom:.9em; }
pre code { background:none; padding:0; }
table { border-collapse:collapse; width:100%; margin-bottom:.9em; }
th,td { border:1px solid #e2e8f0; padding:8px 12px; text-align:left; }
th { background:#f8fafc; font-weight:600; }
blockquote { border-left:4px solid #cbd5e1; margin:0 0 .9em; padding:.5em 1em; color:#475569; }
"""

_BTN_PRIMARY = (
    "QPushButton { background:#3b82f6; color:white; border:none; border-radius:4px;"
    " padding:6px 14px; font-size:13px; } QPushButton:hover { background:#2563eb; }"
)
_BTN_SECONDARY = (
    "QPushButton { background:#1e293b; color:#94a3b8; border:1px solid #334155;"
    " border-radius:4px; padding:6px 14px; font-size:13px; }"
    " QPushButton:hover { border-color:#3b82f6; color:#cbd5e1; }"
)


def _md_to_html(markdown_text: str) -> str:
    """Convert markdown to HTML. Uses markdown-it-py if available, else basic fallback."""
    try:
        from markdown_it import MarkdownIt
        md = MarkdownIt()
        body = md.render(markdown_text)
    except ImportError:
        # basic fallback: wrap in <pre> so content is readable
        import html
        body = f"<pre>{html.escape(markdown_text)}</pre>"
    return f"<html><head><style>{_PREVIEW_CSS}</style></head><body>{body}</body></html>"


class MarkdownView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._markdown: str | None = None

        self._actions_bar = QWidget()
        actions_layout = QHBoxLayout(self._actions_bar)
        actions_layout.setContentsMargins(0, 0, 0, 12)
        actions_layout.setSpacing(8)

        self._btn_copy = QPushButton("Copiar MD")
        self._btn_copy.setStyleSheet(_BTN_PRIMARY)
        self._btn_copy.clicked.connect(self._copy_md)

        self._btn_download = QPushButton("Descargar .md")
        self._btn_download.setStyleSheet(_BTN_SECONDARY)
        self._btn_download.clicked.connect(self._download_md)

        actions_layout.addWidget(self._btn_copy)
        actions_layout.addWidget(self._btn_download)
        actions_layout.addStretch()

        self._actions_bar.setVisible(False)

        # Preview area
        if _HAS_WEBENGINE:
            self._preview = QWebEngineView()
            self._preview.setStyleSheet("border-radius:8px;")
        else:
            from PyQt6.QtWidgets import QTextBrowser
            self._preview = QTextBrowser()
            self._preview.setStyleSheet(
                "background:white; color:#111; border-radius:8px; padding:12px;"
            )

        self._empty_label = QLabel("El resultado aparecerá aquí")
        self._empty_label.setStyleSheet("color:#475569; font-size:14px;")
        self._empty_label.setAlignment(
            __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter
        )

        self._spinner_label = QLabel("Convirtiendo…")
        self._spinner_label.setStyleSheet("color:#64748b; font-size:14px;")
        self._spinner_label.setAlignment(
            __import__("PyQt6.QtCore", fromlist=["Qt"]).Qt.AlignmentFlag.AlignCenter
        )
        self._spinner_label.setVisible(False)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._actions_bar)
        layout.addWidget(self._empty_label)
        layout.addWidget(self._spinner_label)
        layout.addWidget(self._preview)
        self._preview.setVisible(False)

    # ── public API ────────────────────────────────────────────────────────

    def set_loading(self, loading: bool):
        self._spinner_label.setVisible(loading)
        self._empty_label.setVisible(not loading and self._markdown is None)
        self._preview.setVisible(not loading and self._markdown is not None)
        self._actions_bar.setVisible(not loading and self._markdown is not None)

    def set_markdown(self, markdown: str | None):
        self._markdown = markdown
        if markdown is None:
            self._preview.setVisible(False)
            self._actions_bar.setVisible(False)
            self._empty_label.setVisible(True)
            return

        html = _md_to_html(markdown)
        if _HAS_WEBENGINE:
            self._preview.setHtml(html, QUrl("about:blank"))
        else:
            self._preview.setHtml(html)

        self._preview.setVisible(True)
        self._actions_bar.setVisible(True)
        self._empty_label.setVisible(False)

    # ── actions ───────────────────────────────────────────────────────────

    def _copy_md(self):
        if self._markdown:
            QApplication.clipboard().setText(self._markdown)

    def _download_md(self):
        if not self._markdown:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Markdown", "resultado.md", "Markdown (*.md)"
        )
        if path:
            Path(path).write_text(self._markdown, encoding="utf-8")


from pathlib import Path  # noqa: E402 — imported at bottom to avoid circular
