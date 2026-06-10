from pathlib import Path
from unittest.mock import patch, MagicMock


def test_markitdown_convert_returns_string():
    mock_result = MagicMock()
    mock_result.text_content = "# Hello from markitdown"

    with patch("backend.converters.markitdown.MarkItDown") as MockMD:
        MockMD.return_value.convert.return_value = mock_result
        from backend.converters.markitdown import convert
        result = convert(Path("test.pdf"))

    assert result == "# Hello from markitdown"
    MockMD.return_value.convert.assert_called_once_with("test.pdf")


def test_docling_convert_returns_string():
    mock_result = MagicMock()
    mock_result.document.export_to_markdown.return_value = "# Hello from docling"

    with patch("backend.converters.docling.DocumentConverter") as MockDC:
        MockDC.return_value.convert.return_value = mock_result
        from backend.converters.docling import convert
        result = convert(Path("test.pdf"))

    assert result == "# Hello from docling"
    MockDC.return_value.convert.assert_called_once_with(str(Path("test.pdf")))
