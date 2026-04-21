# CSE 3461 Final Project: Python Terminal Chat Application
Authors: Johanana, Julio, Roy

## Feature 1: Broadcast Chat
- Allows direct, broadcast  messaging between connected clients to server
- Use of `prompt_toolkit` and `patch_stdout` to prevent interruptions while client is typing a message.
- Uses  `argparse` for passing IP addresses and ports directly from the terminal.

## Feature 2: Unicast (One-to-one Messaging)
- Allows direct, one-to-one  messaging between connected clients using the `@username message` format.
- Use of `prompt_toolkit` and `patch_stdout` to prevent interruptions while client is typing a message.
- Uses  `argparse` for passing IP addresses and ports directly from the terminal.

## Feature 3: Application-Layer Protocol
- Adds a JSON framing protocol in protocol.py, which fixes a problem where messaged could be split or merged. (JSON keeps data structured)
- Server sends ACK for every delivered message. Client measures and prints RTT.
- client.py and server.py should support both broadcast and unicast
- Proper login handshake with more error handling

## How to Run:
1. Start the server: `python <feature>/server.py [--ip IP] [--port PORT]`
2. Start the clients: `python <feature>/client.py [--ip SERVER_IP] [--port SERVER_PORT]`