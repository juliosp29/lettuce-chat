import argparse
import socket
import threading

from prompt_toolkit import prompt
from prompt_toolkit.patch_stdout import patch_stdout

def handle_server(client_socket: socket.socket) -> None:
    try:
        while True:
            encoded_message = client_socket.recv(1024)
            
            # If empty bytes, then the server has disconnected
            if not encoded_message: break 
            decoded_message = encoded_message.decode("utf-8").strip()
            print(decoded_message)
    except ConnectionResetError:
        print("\n[Client] Server forcefully disconnected.")
    except Exception as e:
        print(f"\n[Client] Error receiving message: {e}")

def start_client(server_ip_address: str, server_port: int) -> None:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client_socket.connect((server_ip_address, server_port))
    except Exception as e:
        print(f"[Client] Unable to connect to server: {e}")
        return
    
    print(f"[Client] Successfully connected to server at {server_ip_address}")

    username_request_bytes = client_socket.recv(1024)
    username_request = username_request_bytes.decode("utf-8")
    username = prompt(username_request)
    
    client_socket.sendall(username.encode("utf-8"))

    thread = threading.Thread(target=handle_server, args=(client_socket,))
    thread.start()

    try:
        with patch_stdout():
            while True:
                message = prompt("Enter message: ")
                encoded_message = message.encode("utf-8")
                client_socket.sendall(encoded_message)
    except KeyboardInterrupt:
        print(f"[Client] Shutting down.")
    finally:
        client_socket.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client initialization for unicast messaging")
    parser.add_argument("ip", type=str, help="The IP Address of the SERVER you are trying to connect to.")
    parser.add_argument("port", type=int, help="The port number that the SERVER will listen from")

    args = parser.parse_args()
    start_client(server_ip_address=args.ip, server_port=args.port)