import socket
import threading
import argparse

from protocol import send_frame, recv_frame, build_message


username_to_conn: dict[str, socket.socket] = {}  # { username: socket }
conn_lock = threading.Lock()


def _safe_send(conn: socket.socket, msg: dict) -> bool:
    try:
        send_frame(conn, msg)
        return True
    except (ConnectionError, OSError):
        return False


def handle_client(client_conn: socket.socket, username: str) -> None:
    try:
        while True:
            msg = recv_frame(client_conn)
            msg_type = msg.get("type")

            if msg_type == "MSG":
                target = msg.get("target")
                seq = msg.get("seq", 0)

                if target is None:
                    # broadcast: forward to every other registered client
                    with conn_lock:
                        recipients = [(u, c) for u, c in username_to_conn.items()
                                      if u != username]
                    for _, conn in recipients:
                        _safe_send(conn, msg)
                    send_frame(client_conn, build_message("ACK", seq=seq))

                elif target in username_to_conn:
                    # unicast
                    send_frame(username_to_conn[target], msg)
                    send_frame(client_conn, build_message("ACK", seq=seq))

                else:
                    send_frame(client_conn, build_message(
                        "ERROR", seq=seq,
                        payload=f"unknown user: {target}"))

            elif msg_type == "PING":
                send_frame(client_conn, build_message("ACK", seq=msg.get("seq", 0)))

            else:
                send_frame(client_conn, build_message(
                    "ERROR", payload=f"unknown message type: {msg_type}"))

    except ConnectionError:
        pass
    except Exception as e:
        print(f"[Server] Error handling {username}: {e}")
    finally:
        print(f"[Server] {username} disconnected.")
        with conn_lock:
            username_to_conn.pop(username, None)
        client_conn.close()


def _do_login(client_conn: socket.socket) -> str | None:
    """Run the login handshake. Returns username or None on failure."""
    try:
        send_frame(client_conn, build_message(
            "LOGIN", payload="Please enter your username:"))
        reply = recv_frame(client_conn)
    except ConnectionError:
        return None

    username = (reply.get("payload") or "").strip()

    if not username:
        _safe_send(client_conn, build_message(
            "ERROR", payload="username cannot be empty"))
        return None

    with conn_lock:
        if username in username_to_conn:
            _safe_send(client_conn, build_message(
                "ERROR", payload=f"username '{username}' is already taken"))
            return None
        username_to_conn[username] = client_conn

    return username


def start_server(ip_address: str, port: int) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((ip_address, port))
    server_socket.listen()

    print(f"[Server] Listening on {ip_address}:{port}")

    try:
        while True:
            client_conn, address = server_socket.accept()
            print(f"[Server] Accepted connection from {address}")

            username = _do_login(client_conn)
            if username is None:
                client_conn.close()
                continue

            print(f"[Server] User '{username}' registered.")
            t = threading.Thread(
                target=handle_client,
                args=(client_conn, username),
                daemon=True,
            )
            t.start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Feature 3 framed chat server")
    parser.add_argument("--ip", type=str, default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5555)
    args = parser.parse_args()
    start_server(ip_address=args.ip, port=args.port)
