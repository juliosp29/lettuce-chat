# Algorithm 4: High-Level Client Logic — One-to-One Chat (Feature 2)
#
# Create a TCP client socket
# Connect to the server using the provided IP address and port
# Wait for the server to request a username
# Input the username from the user and send it to the server
#
# Start a background thread to continuously:
#     Receive incoming messages from the server
#     Display the received messages to the user
#
# In the main thread, repeatedly:
#     Accept user input from the keyboard
#     To send a private message, type in the format @username message
#     Send the message to the server for delivery to the target user
#
# If the server disconnects or an error occurs, close the socket connection
