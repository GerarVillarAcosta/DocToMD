from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QButtonGroup, QHBoxLayout, QPushButton, QWidget

_ENGINES = {
    "markitdown": "Rápido, ideal para documentos simples y estructurados (Microsoft MarkItDown)",
    "docling": "Alta fidelidad para PDFs densos con tablas y layouts complejos (IBM Docling)",
}

_BTN_ACTIVE = (
    "QPushButton { background:#1d3a60; color:#3b82f6; border:1px solid #3b82f6;"
    " border-radius:4px; padding:4px 14px; font-size:12px; }"
)
_BTN_IDLE = (
    "QPushButton { background:#1e293b; color:#94a3b8; border:1px solid #334155;"
    " border-radius:4px; padding:4px 14px; font-size:12px; }"
    "QPushButton:hover { border-color:#3b82f6; color:#cbd5e1; }"
)


class EngineToggle(QWidget):
    engine_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "markitdown"
        self._buttons: dict[str, QPushButton] = {}

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        group = QButtonGroup(self)
        group.setExclusive(True)

        for engine, tooltip in _ENGINES.items():
            btn = QPushButton(engine)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setChecked(engine == self._current)
            btn.setStyleSheet(_BTN_ACTIVE if engine == self._current else _BTN_IDLE)
            btn.clicked.connect(lambda checked, e=engine: self._select(e))
            group.addButton(btn)
            layout.addWidget(btn)
            self._buttons[engine] = btn

    def _select(self, engine: str):
        if engine == self._current:
            return
        self._current = engine
        for e, btn in self._buttons.items():
            btn.setStyleSheet(_BTN_ACTIVE if e == engine else _BTN_IDLE)
        self.engine_changed.emit(engine)

    @property
    def current_engine(self) -> str:
        return self._current
