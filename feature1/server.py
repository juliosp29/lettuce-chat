import socket
import threading
import argparse

clients_lock = threading.Lock()  # Lock to synchronize access to the clients list
clients: list[socket.socket] = []  # List to store connected client sockets

def broadcast(message: str, sender_socket: socket.socket) -> None:
    with clients_lock:
        targets = [s for s in clients if s is not sender_socket]
    for sock in targets:
        try:
            sock.sendall(message.encode("utf-8"))
        except Exception:
            pass

def handle_client(connection: socket.socket, address: tuple) -> None:
    print(f"[+] Client connected: {address}")
    broadcast(f"[Server] A new client {address} has joined the chat.\n", connection)

    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            message = f"[{address[0]}:{address[1]}] {data.decode('utf-8').strip()}\n"
            broadcast(message, connection)
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        with clients_lock:
            if connection in clients:
                clients.remove(connection)
        print(f"[-] Client disconnected: {address}")
        broadcast(f"[Server] Client {address} has left the chat.\n", connection)
        connection.close() 

def start_server(host: str, port: int) -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(10)
    print(f"[Server] Listening on {host}:{port} ...")

    try:
        while True:
            connection, address = server_sock.accept()
            with clients_lock:
                clients.append(connection)
            t = threading.Thread(target=handle_client, args=(connection, address), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down.")
    finally:
        server_sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server initialization for unicast messaging")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="The IP Address of the server")
    parser.add_argument("--port", type=int, default=5555, help="The port number to listen from")

    args = parser.parse_args()
    start_server(host=args.ip, port=args.port)