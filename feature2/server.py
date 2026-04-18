import socket
import threading
import argparse

username_to_socket = {} # { username: socket }

def handle_client(client_socket: socket.socket, username: str) -> None:
    try:
        while True:
            message_bytes = client_socket.recv(1024)
            
            # If empty bytes, then the client has disconnected
            if not message_bytes: break
            decoded_message = message_bytes.decode("utf-8").strip()
            
            # Empty string check
            if not decoded_message: continue
                
            message_parts = decoded_message.split(maxsplit=1)
            target_token = message_parts[0]

            if target_token.startswith("@") and len(target_token) > 1:
                target_username = target_token[1:]
                if target_username in username_to_socket:
                    message = f"[{username}]: {decoded_message}\n"
                    username_to_socket[target_username].sendall(message.encode("utf-8"))
                else:
                    client_socket.sendall(b"[Server] Target username was not recognized\n")
            else:
                client_socket.sendall(b"[Server] FORMAT ERROR: Please begin your message with: @<username> <message>\n")
    except ConnectionResetError:
        print(f"[Server] ConnectionResetError with {username}")
        pass 
    finally:
        print(f"[Server] {username} disconnected.")
        username_to_socket.pop(username, None)
        client_socket.close()

def start_server(ip_address: str, port: int) -> None:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((ip_address, port))
    server_socket.listen()
    
    print(f"[Server] Listening on {ip_address}:{port}")

    try:
        while True:
            client_socket, address = server_socket.accept()
            print(f"[Server] Accepted connection from {address}")

            client_socket.sendall(b"[Server] Successfully connected. Please enter your username: ")

            response_bytes = client_socket.recv(1024)
            username = response_bytes.decode("utf-8").strip()
            
            username_to_socket[username] = client_socket
            print(f"[Server] User '{username}' registered.")

            client_comm_thread = threading.Thread(target=handle_client, args=(client_socket, username))
            client_comm_thread.start()
    except KeyboardInterrupt:
        print("\n[Server] Shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server initialization for unicast messaging")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="The IP Address of the server")
    parser.add_argument("--port", type=int, default=5555, help="The port number to listen from")

    args = parser.parse_args()
    start_server(ip_address=args.ip, port=args.port)