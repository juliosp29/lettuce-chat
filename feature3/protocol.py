"""
Feature 3 — Application-Layer Framing Protocol

Wire format for every message on the socket:

    [ 4-byte big-endian length N ][ N bytes of UTF-8 JSON body ]

The JSON body is a dict with this schema:

    {
        "type":         "MSG" | "LOGIN" | "ACK" | "ERROR" | "PING",
        "seq":          int,          # per-sender counter, increments each send
        "timestamp_ms": int,          # time.time_ns() // 1_000_000 at send time
        "sender":       str | None,   # username of the sender
        "target":       str | None,   # username of recipient, None = broadcast
        "payload":      str           # the actual message text
    }

This fixes the "sticky packets" problem in feature 2 by making every
message framed: the receiver always reads EXACTLY N bytes regardless
of how TCP fragments or coalesces data.
"""

import json
import socket
import struct
import time


# helper that reads EXACTLY n bytes from the socket
def _recvall(sock: socket.socket, n: int) -> bytes:
    # initialize the buffer
    buff = bytearray()
    while len(buff) < n:
        # n - len(buff) is the bytes we still need
        # Guarantees bytes aren't stolen that belong to a different frame
        chunk = sock.recv(n - len(buff))
        if not chunk:
            raise ConnectionError("socket closed mid-frame")
        # add to the buffer
        buff.extend(chunk)
    return bytes(buff)


#helper that serializes a dict and sends it as ONE framed message
def send_frame(sock: socket.socket, msg: dict) -> None:
    # create the body
    body = json.dumps(msg).encode('utf-8')
    # create the header
    header = struct.pack("!I", len(body))
    # sends header+body
    sock.sendall(header + body)
    


# helper that reads ONE framed message off the socket
def recv_frame(sock: socket.socket) -> dict:
    # reads 4 bytes
    header = _recvall(sock, 4)
    # parses thru 4 bytes
    (length,) = struct.unpack("!I", header)
    # know frame size, read those amount of bytes
    body = _recvall(sock, length)
    # bytes->str->dict
    return json.loads(body.decode("utf-8"))


# builds a dict with the standard schema; auto-fills timestamp_ms
def build_message(
    msg_type: str,
    seq: int = 0,
    sender: str | None = None,
    target: str | None = None,
    payload: str = "",
) -> dict:
    return {
        "type": msg_type,
        "seq": seq,
        "timestamp_ms": time.time_ns() // 1_000_000,
        "sender": sender,
        "target": target,
        "payload": payload,
    }


if __name__ == "__main__":
    a, b = socket.socketpair()
    try:
        sent = build_message("MSG", seq=1, sender="alice",
                             target="bob", payload="A" * 5000)
        send_frame(a, sent)
        received = recv_frame(b)
        assert received["payload"] == sent["payload"], "payload mismatch"
        assert len(received["payload"]) == 5000, "length mismatch"
        print(f"OK: round-tripped {len(received['payload'])}-char payload intact")
    finally:
        a.close()
        b.close()
