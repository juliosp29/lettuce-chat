import socket
import threading
import argparse

from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout

def receive_messages(sock: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[Client] Server closed the connection.")
                stop_event.set()
                break
            print(data.decode("utf-8").strip())
        except Exception:
            if not stop_event.is_set():
                print("\n[Client] Lost connection to server.")
            stop_event.set()
            break

def start_client(server_ip: str, port: int) -> None:
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_sock.connect((server_ip, port))
    except Exception as e:
        print(f"[Client] Could not connect to server: {e}")
        return

    local_ip, local_port = client_sock.getsockname()
    print(f"[Client] Connected to server at {server_ip}:{port} from local address {local_ip}:{local_port}")

    stop_event = threading.Event()
    recv_thread = threading.Thread(target=receive_messages, args=(client_sock, stop_event), daemon=True)
    recv_thread.start()

    try:
        with patch_stdout():
            while not stop_event.is_set():
                message = prompt("Enter message: ")
                if stop_event.is_set():
                    break
                if message.strip().lower() == "/quit":
                    print("[Client] Exiting chat...")
                    break
                if not message.strip():
                    continue
                try:
                    client_sock.sendall(message.encode("utf-8"))
                except Exception:
                    print("\n[Client] Failed to send message. Connection may be lost.")
                    break

    except (KeyboardInterrupt, EOFError):
        print("\n[Client] Exiting chat...")
    finally:
        stop_event.set()
        client_sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client initialization for Broadcast messaging")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="The IP Address of the SERVER")
    parser.add_argument("--port", type=int, default=5555, help="The port number of the SERVER")

    args = parser.parse_args()
    start_client(server_ip=args.ip, port=args.port)