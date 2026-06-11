from pathlib import Path
from docling.document_converter import DocumentConverter


def convert(file_path: Path) -> str:
    converter = DocumentConverter()
    result = converter.convert(str(file_path))
    return result.document.export_to_markdown()
