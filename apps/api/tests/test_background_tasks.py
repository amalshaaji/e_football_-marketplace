import json
import struct
from types import SimpleNamespace

import pytest

from app.jobs import tasks


def test_png_dimension_reader_extracts_size() -> None:
    header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 320, 240)
    assert tasks._read_image_dimensions(header) == (320, 240, "PNG")


def test_image_job_writes_metadata_with_checksum(tmp_path, monkeypatch) -> None:
    header = b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", 320, 240)
    (tmp_path / "squad.png").write_bytes(header)
    monkeypatch.setattr(tasks, "get_settings", lambda: SimpleNamespace(media_root=str(tmp_path)))

    tasks.process_image({"path": "squad.png"})

    result = json.loads((tmp_path / "squad.png.metadata.json").read_text())
    assert result["format"] == "PNG"
    assert result["width"] == 320
    assert result["height"] == 240
    assert len(result["sha256"]) == 64


def test_image_job_rejects_paths_outside_media_root(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(tasks, "get_settings", lambda: SimpleNamespace(media_root=str(tmp_path)))
    with pytest.raises(ValueError):
        tasks.process_image({"path": "../outside.png"})
