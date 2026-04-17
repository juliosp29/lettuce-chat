# Algorithm 1: High-Level Server Logic — Broadcast Feature
#
# Create a TCP server socket and bind it to an IP address and port
# Start listening for incoming client connections
# Initialize an empty list to store connected clients
#
# while server is running:
#     Accept a new client connection
#     Add the client to the list of active clients
#     Start a new thread to handle communication with that client
# end while
#
# Client Handler (in each thread):
# Continuously receive messages from the assigned client
# For each received message, forward it to all other connected clients
# If the client disconnects, close the connection and remove it from the list

import socket
import threading
clients_lock = threading.Lock()  # Lock to synchronize access to the clients list
clients: list[socket.socket] = []  # List to store connected client sockets

def broadcast(message: str, sender_socket: socket.socket) -> None:
    with clients_lock:
        targets = [s for s in clients if s is not sender_socket]
    for sock in targets:
        try:
            sock.sendall(message.encode())
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
            message = f"[{address[0]}:{address[1]}] {data.decode().strip()}\n"
            print(f"[BROADCAST] {message.strip()}")
            broadcast(message, connection)
    except (ConnectionResetError, BrokenPipeError):
        pass
    finally:
        with clients_lock:
            if connection in clients:
                clients.remove(connection)
        connection.close()
        print(f"[-] Client disconnected: {address}")
        broadcast(f"[Server] Client {address} has left the chat.\n", connection)

def start_server(host: str = "0.0.0.0", port: int = 5555) -> None:
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(10)
    print(f"[Server] Listening on {host}:{port} ...")

    try:
        while True:
            connection, address= server_sock.accept()
            with clients_lock:
                clients.append(connection)
            # Each client gets its own thread
            t = threading.Thread(target=handle_client, args=(connection, address), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down.")
    finally:
        server_sock.close()


if __name__ == "__main__":
    start_server()