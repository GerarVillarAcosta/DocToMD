from pathlib import Path
from markitdown import MarkItDown


def convert(file_path: Path) -> str:
    md = MarkItDown()
    result = md.convert(str(file_path))
    return result.text_content
