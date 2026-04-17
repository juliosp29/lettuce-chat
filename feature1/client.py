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
