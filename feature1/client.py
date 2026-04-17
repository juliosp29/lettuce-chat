# Algorithm 2: High-Level Client Logic — Broadcast Application
#
# Create a TCP client socket
# Connect to the server using the server's IP address and port
# Display the client's local address and port information
#
# Start a background thread to continuously:
#     Receive incoming messages from the server
#     Display received messages to the user
#
# In the main thread, repeatedly:
#     Accept user input from the keyboard
#     Send the typed message to the server
#
# If the server disconnects or an error occurs, close the connection
import socket
import threading
import sys

def receive_messages(sock: socket.socket, stop_event: threading.Event) -> None:
    while not stop_event.is_set():
        try:
            data = sock.recv(4096)
            if not data:
                print("\n[Client] Server close the connection.")
                stop_event.set()
                break
            print(data.decode(), end="", flush=True)
        except Exception:
            if not stop_event.is_set():
                print("\n[Client] Lost connection to server.")
            stop_event.set()
            break

def start_client(server_ip: str = "127.0.0.1", port: int = 5555) -> None:
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
        while not stop_event.is_set():
            message = input()
            if stop_event.is_set():
                break
            if message.strip().lower() == "/quit":
                print("[Client] Exiting chat...")
                break
            if not message.strip():
                continue
            try:
                client_sock.sendall(message.encode())
            except Exception:
                print("\n[Client] Failed to send message. Connection may be lost.")
                break

    except (KeyboardInterrupt, EOFError):
        print("\n[Client] Exiting chat...")
    finally:
        stop_event.set()
        client_sock.close()

if __name__ == "__main__":
    server_ip = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5555
    start_client(server_ip, port)