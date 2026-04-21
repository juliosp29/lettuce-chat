import argparse
import itertools
import socket
import threading
import time

from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout

from protocol import send_frame, recv_frame, build_message


# Per-sender sequence counter — increments every time we send a MSG.
_seq_counter = itertools.count(1)

# seq -> send time in ms. Used to compute RTT when matching ACK arrives.
_pending_sends: dict[int, int] = {}
_pending_lock = threading.Lock()


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def listen_to_server(client_socket: socket.socket) -> None:
    try:
        while True:
            msg = recv_frame(client_socket)
            msg_type = msg.get("type")

            if msg_type == "MSG":
                sender = msg.get("sender") or "?"
                print(f"[{sender}]: {msg.get('payload', '')}")

            elif msg_type == "ACK":
                seq = msg.get("seq", 0)
                with _pending_lock:
                    sent_at = _pending_sends.pop(seq, None)
                if sent_at is not None:
                    rtt = _now_ms() - sent_at
                    print(f"[RTT] seq={seq} rtt={rtt}ms")

            elif msg_type == "ERROR":
                print(f"[Server ERROR] {msg.get('payload', '')}")

            else:
                print(f"[Client] Unknown message type: {msg_type}")

    except ConnectionError:
        print("\n[Client] Server closed the connection.")
    except Exception as e:
        print(f"\n[Client] Error receiving message: {e}")


def _parse_target(raw: str) -> tuple[str | None, str] | None:
    """Parse '@user message' into (user, message). Returns None if malformed."""
    if not raw.startswith("@"):
        return (None, raw)                # broadcast

    parts = raw.split(maxsplit=1)
    token = parts[0]
    if len(token) <= 1 or len(parts) < 2 or not parts[1].strip():
        return None                       # malformed

    return (token[1:], parts[1])


def start_client(server_ip_address: str, server_port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip_address, server_port))
    except Exception as e:
        print(f"[Client] Unable to connect to server: {e}")
        return

    print(f"[Client] Connected to {server_ip_address}:{server_port}")

    # login handshake
    try:
        login_req = recv_frame(client_socket)
    except ConnectionError:
        print("[Client] Server closed connection before login.")
        return

    if login_req.get("type") != "LOGIN":
        print(f"[Client] Expected LOGIN, got {login_req.get('type')}")
        client_socket.close()
        return

    username = prompt(login_req.get("payload", "Username:") + " ").strip()
    if not username:
        print("[Client] Empty username, exiting.")
        client_socket.close()
        return

    send_frame(client_socket, build_message(
        "LOGIN", sender=username, payload=username))

    thread = threading.Thread(
        target=listen_to_server, args=(client_socket,), daemon=True)
    thread.start()

    try:
        with patch_stdout():
            while True:
                raw = prompt("Enter message: ")
                if not raw.strip():
                    continue

                parsed = _parse_target(raw)
                if parsed is None:
                    print("[Client] Usage: @username message  (or type a message for broadcast)")
                    continue
                target, payload = parsed

                seq = next(_seq_counter)
                with _pending_lock:
                    _pending_sends[seq] = _now_ms()

                try:
                    send_frame(client_socket, build_message(
                        "MSG", seq=seq, sender=username,
                        target=target, payload=payload))
                except (ConnectionError, OSError):
                    print("[Client] Connection lost.")
                    break

    except (KeyboardInterrupt, EOFError):
        print("[Client] Shutting down.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature 3 framed chat client")
    parser.add_argument("ip", type=str, help="Server IP address")
    parser.add_argument("port", type=int, help="Server port")
    args = parser.parse_args()
    start_client(server_ip_address=args.ip, server_port=args.port)
