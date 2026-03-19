"""
Disk and file utility helpers.

Currently provides basic session persistence utilities as optional helpers.
In this pre-RAG version, the app uses in-memory session storage, but these
utilities are available if you want to optionally dump sessions to disk for
debugging or simple persistence.

None of these are called automatically — they are opt-in utilities.
"""

import json
import os
from pathlib import Path
from typing import Any

from core.logger import get_logger

logger = get_logger(__name__)

# Default directory for any disk-based session dumps
_DEFAULT_SESSIONS_DIR = Path("./session_dumps")


def ensure_directory(path: Path) -> None:
    """
    Create a directory (and parents) if it does not exist.
    Safe to call even if the directory already exists.
    """
    path.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Directory ensured: {path}")


def write_json(filepath: Path, data: Any) -> None:
    """
    Write a Python object as JSON to a file.
    Creates parent directories if needed.

    Args:
        filepath: Full path including filename, e.g. Path("./data/session.json")
        data:     Any JSON-serializable Python object.
    """
    ensure_directory(filepath.parent)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.debug(f"JSON written: {filepath}")


def read_json(filepath: Path) -> Any:
    """
    Read and return the contents of a JSON file.

    Args:
        filepath: Path to the JSON file.

    Returns:
        Parsed Python object.

    Raises:
        FileNotFoundError: If the file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    logger.debug(f"JSON read: {filepath}")
    return data


def dump_session_to_disk(session_id: str, history: list[dict]) -> Path:
    """
    Optionally dump a session's conversation history to a JSON file on disk.
    Useful for debugging or manual inspection.

    Args:
        session_id: The session identifier (used as filename).
        history:    List of message dicts (role + content).

    Returns:
        The path where the file was written.
    """
    safe_name = session_id.replace("/", "_").replace("\\", "_")
    filepath = _DEFAULT_SESSIONS_DIR / f"{safe_name}.json"
    write_json(filepath, {"session_id": session_id, "history": history})
    logger.info(f"Session dumped to disk: {filepath}")
    return filepath


def file_exists(filepath: Path) -> bool:
    """
    Check whether a file exists at the given path.
    """
    return filepath.is_file()
