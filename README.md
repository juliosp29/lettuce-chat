# CSE 3461 Final Project: Python Terminal Chat Application
**Authors:** Johanan, Julio, Roy

## Feature 1: Broadcast Chat
- Enables broadcast messaging where any connected client can send a message to all other clients through the server.
- Uses `prompt_toolkit` and `patch_stdout` to prevent incoming messages from interrupting the user while typing.
- Uses `argparse` to allow IP addresses and ports to be passed directly from the terminal.

## Feature 2: Unicast (One-to-One Messaging)
- Enables private messaging between two specific clients using the `@username message` format.
- Uses `prompt_toolkit` and `patch_stdout` to prevent incoming messages from interrupting the user while typing.
- Uses `argparse` to allow IP addresses and ports to be passed directly from the terminal.

## Feature 3: Application-Layer Protocol
- Adds a JSON framing protocol in `protocol.py` that ensures messages are never split or merged across TCP packets, keeping all data structured and intact.
- Server sends an ACK for every delivered message; the client measures and displays the round-trip time (RTT).
- Both `client.py` and `server.py` support broadcast and unicast messaging.
- Includes a login handshake with improved error handling for a more reliable connection setup.

## How to Run
1. Start the server: `python <feature>/server.py [--ip IP] [--port PORT]`
2. Start a client: `python <feature>/client.py [--ip SERVER_IP] [--port SERVER_PORT]`
