"""
Secure File Handling & Temporary File Utilities.
Sanitizes filenames to prevent path traversal and ensures guaranteed cleanup
of temporary export artifacts.
"""

import os
import re
import uuid
import tempfile
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Temporary directory for export artifacts
TEMP_EXPORT_DIR = Path(tempfile.gettempdir()) / "ai_doc_generator_exports"
TEMP_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

def sanitize_filename(title: Optional[str], default_name: str = "document", extension: str = "") -> str:
    """
    Sanitizes user-provided or document titles into a filesystem-safe filename.
    Removes path traversal sequences ('../', '..\\'), null bytes, and illegal characters.
    """
    if not title or not title.strip():
        base = default_name
    else:
        # Strip path components and null bytes
        clean = os.path.basename(title).replace("\0", "")
        # Remove directory traversal sequences
        clean = clean.replace("..", "").replace("/", "").replace("\\", "")
        # Replace non-alphanumeric characters (except dashes and underscores) with hyphen
        clean = re.sub(r"[^\w\s\-_]", "", clean).strip()
        # Collapse multiple spaces or hyphens
        clean = re.sub(r"[-\s]+", "-", clean)
        base = clean if clean else default_name

    # Truncate length to 80 chars to avoid OS MAX_PATH issues
    base = base[:80].strip("-")
    if not base:
        base = default_name

    ext = extension.lstrip(".")
    if ext:
        return f"{base}.{ext}"
    return base

def get_temp_export_path(prefix: str = "export", extension: str = "tmp") -> str:
    """
    Generates an isolated, collision-free temporary file path in the export temp directory.
    """
    ext = extension.lstrip(".")
    unique_id = uuid.uuid4().hex[:12]
    filename = f"{prefix}_{unique_id}.{ext}"
    return str(TEMP_EXPORT_DIR / filename)

def cleanup_file(filepath: Optional[str]):
    """
    Safely removes a temporary file. Used as a FastAPI BackgroundTask.
    """
    if not filepath:
        return
    try:
        p = Path(filepath)
        if p.exists() and p.is_file():
            p.unlink()
            logger.debug(f"Temporary file cleaned up: {filepath}")
    except Exception as e:
        logger.warning(f"Failed to delete temporary file {filepath}: {e}")
