# Algorithm 2 High-level Client Logic for broadcast application

# 1: Create a TCP client socket
# 2: Connect to the server using the server’s IP address and port
# 3: Display the client’s local address and port information

# 4: Start a background thread to continuously:

# • Receive incoming messages from the server
# • Display received messages to the user

# 5: In the main thread, repeatedly:

# • Accept user input from the keyboard
# • Send the typed message to the server

# 6: If the server disconnects or an error occurs, close the connection
