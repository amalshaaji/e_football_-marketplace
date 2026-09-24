"""Small Redis RESP2 queue adapter using only the Python standard library."""

import json
import socket
from urllib.parse import unquote, urlparse

from app.core.config import get_settings

QUEUE_KEY = "efootball:jobs"
PROCESSING_KEY = "efootball:jobs:processing"
DEAD_KEY = "efootball:jobs:dead"


class RedisProtocolError(RuntimeError):
    pass


def _encode(parts: list[str | bytes]) -> bytes:
    encoded = [part if isinstance(part, bytes) else part.encode() for part in parts]
    return b"*" + str(len(encoded)).encode() + b"\r\n" + b"".join(
        b"$" + str(len(part)).encode() + b"\r\n" + part + b"\r\n" for part in encoded
    )


def _read_response(stream):
    line = stream.readline()
    if not line:
        raise RedisProtocolError("Redis closed the connection")
    marker, value = line[:1], line[1:-2]
    if marker == b"+":
        return value.decode()
    if marker == b"-":
        raise RedisProtocolError(value.decode())
    if marker == b":":
        return int(value)
    if marker == b"$":
        length = int(value)
        if length == -1:
            return None
        data = stream.read(length)
        stream.read(2)
        return data
    if marker == b"*":
        length = int(value)
        return None if length == -1 else [_read_response(stream) for _ in range(length)]
    raise RedisProtocolError("Unknown Redis response type")


class RedisConnection:
    def __init__(self, timeout: float = 5) -> None:
        parsed = urlparse(get_settings().redis_url)
        if parsed.scheme != "redis" or not parsed.hostname:
            raise ValueError("REDIS_URL must use redis://host:port/db")
        self.host = parsed.hostname
        self.port = parsed.port or 6379
        self.password = unquote(parsed.password) if parsed.password else None
        self.database = parsed.path.strip("/") or "0"
        self.timeout = timeout

    def command(self, *parts: str | bytes):
        with socket.create_connection((self.host, self.port), timeout=self.timeout) as connection:
            stream = connection.makefile("rwb")
            if self.password:
                stream.write(_encode(["AUTH", self.password]))
                stream.flush()
                _read_response(stream)
            if self.database != "0":
                stream.write(_encode(["SELECT", self.database]))
                stream.flush()
                _read_response(stream)
            stream.write(_encode(list(parts)))
            stream.flush()
            return _read_response(stream)


class RedisJobQueue:
    def __init__(self) -> None:
        self.redis = RedisConnection(timeout=35)

    def enqueue(self, name: str, payload: dict, *, attempts: int = 0, job_id: str | None = None) -> str:
        import uuid

        job_id = job_id or str(uuid.uuid4())
        job = json.dumps({"id": job_id, "name": name, "payload": payload, "attempts": attempts}, separators=(",", ":"))
        self.redis.command("LPUSH", QUEUE_KEY, job)
        return job_id

    def reserve(self, timeout: int = 30) -> dict | None:
        raw = self.redis.command("BRPOPLPUSH", QUEUE_KEY, PROCESSING_KEY, str(timeout))
        return json.loads(raw) if raw else None

    def acknowledge(self, job: dict) -> None:
        self.redis.command("LREM", PROCESSING_KEY, "1", json.dumps(job, separators=(",", ":")))

    def retry(self, job: dict) -> None:
        self.acknowledge(job)
        self.redis.command("LPUSH", QUEUE_KEY, json.dumps(job, separators=(",", ":")))

    def dead_letter(self, job: dict) -> None:
        self.acknowledge(job)
        self.redis.command("LPUSH", DEAD_KEY, json.dumps(job, separators=(",", ":")))

    def requeue_abandoned(self) -> int:
        count = 0
        while True:
            job = self.redis.command("RPOPLPUSH", PROCESSING_KEY, QUEUE_KEY)
            if job is None:
                return count
            count += 1


def enqueue_notification(user_id, event_type: str, payload: dict) -> str:
    return RedisJobQueue().enqueue(
        "notification.persist",
        {"user_id": str(user_id), "event_type": event_type, "payload": payload},
    )
