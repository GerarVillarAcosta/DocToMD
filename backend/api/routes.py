import asyncio
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, UploadFile
from backend.converters import docling, markitdown

router = APIRouter()

SUPPORTED = {".pdf", ".docx", ".pptx", ".xlsx", ".png", ".jpg", ".jpeg", ".webp"}
ENGINES = {"markitdown": markitdown, "docling": docling}
_pool = ThreadPoolExecutor(max_workers=2)


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/convert")
async def convert(file: UploadFile, engine: str = Form(default="markitdown")):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in SUPPORTED:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {suffix}")
    if engine not in ENGINES:
        raise HTTPException(status_code=400, detail=f"Unknown engine: {engine}")

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)

    try:
        loop = asyncio.get_event_loop()
        markdown = await asyncio.wait_for(
            loop.run_in_executor(_pool, ENGINES[engine].convert, tmp_path),
            timeout=120.0,
        )
    except asyncio.TimeoutError:
        raise HTTPException(status_code=504, detail="Conversion timed out after 120s")
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    finally:
        tmp_path.unlink(missing_ok=True)

    return {"markdown": markdown, "engine": engine, "filename": file.filename}
