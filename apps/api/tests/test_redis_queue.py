from io import BytesIO

from app.jobs.queue import _encode, _read_response


def test_redis_command_uses_resp_bulk_array_encoding() -> None:
    assert _encode(["LPUSH", "queue", "value"]) == b"*3\r\n$5\r\nLPUSH\r\n$5\r\nqueue\r\n$5\r\nvalue\r\n"


def test_redis_resp_parser_handles_nested_array_and_bulk_strings() -> None:
    response = b"*2\r\n$5\r\nqueue\r\n$5\r\nvalue\r\n"
    assert _read_response(BytesIO(response)) == [b"queue", b"value"]


def test_redis_resp_parser_handles_null_and_integer() -> None:
    assert _read_response(BytesIO(b"$-1\r\n")) is None
    assert _read_response(BytesIO(b":3\r\n")) == 3
