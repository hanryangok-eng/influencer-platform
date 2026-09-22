import json
import os
import re
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path


DATA_ROOT = Path(os.getenv("KBP_DATA_DIR", ".kbp_data")).resolve()


def _job_dir(job_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "", job_id)
    if not safe:
        raise ValueError("invalid job id")
    return DATA_ROOT / safe


def _atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def new_job(config: dict) -> str:
    now = datetime.now(timezone.utc)
    job_id = f"{now:%Y%m%dT%H%M%SZ}-{uuid.uuid4().hex[:8]}"
    _atomic_json(_job_dir(job_id) / "status.json", {
        "job_id": job_id,
        "status": "running",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "progress_done": 0,
        "progress_total": 0,
        "config": config,
    })
    return job_id


def save_checkpoint(job_id: str, state: dict) -> None:
    folder = _job_dir(job_id)
    _atomic_json(folder / "checkpoint.json", state)
    status = load_status(job_id) or {"job_id": job_id, "created_at": datetime.now(timezone.utc).isoformat()}
    status.update({
        "status": "running",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "progress_done": state.get("progress_done", 0),
        "progress_total": state.get("progress_total", 0),
        "records": len(state.get("records", [])),
    })
    _atomic_json(folder / "status.json", status)


def save_result(job_id: str, payload: dict, excel_bytes: bytes) -> None:
    folder = _job_dir(job_id)
    _atomic_json(folder / "result.json", payload)
    excel_path = folder / "result.xlsx"
    excel_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix="result", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(excel_bytes)
        os.replace(temporary, excel_path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    status = load_status(job_id) or {"job_id": job_id}
    status.update({
        "status": "completed",
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "records": len(payload.get("records", [])),
        "sendable": payload.get("summary", {}).get("sendable", 0),
        "filename": payload.get("download_filename", "GLOEUM_해외바이어.xlsx"),
    })
    _atomic_json(folder / "status.json", status)


def mark_failed(job_id: str, message: str) -> None:
    status = load_status(job_id) or {"job_id": job_id}
    status.update({"status": "interrupted", "updated_at": datetime.now(timezone.utc).isoformat(), "message": message[:500]})
    _atomic_json(_job_dir(job_id) / "status.json", status)


def load_status(job_id: str) -> dict | None:
    path = _job_dir(job_id) / "status.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_checkpoint(job_id: str) -> dict | None:
    path = _job_dir(job_id) / "checkpoint.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def load_result(job_id: str) -> tuple[dict | None, bytes | None]:
    folder = _job_dir(job_id)
    try:
        payload = json.loads((folder / "result.json").read_text(encoding="utf-8"))
        excel = (folder / "result.xlsx").read_bytes()
        return payload, excel
    except (OSError, json.JSONDecodeError):
        return None, None


def list_jobs(limit: int = 20) -> list[dict]:
    if not DATA_ROOT.exists():
        return []
    rows = [load_status(path.name) for path in DATA_ROOT.iterdir() if path.is_dir()]
    rows = [row for row in rows if row]
    rows.sort(key=lambda row: row.get("updated_at", ""), reverse=True)
    return rows[:limit]
