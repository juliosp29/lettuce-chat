# Algorithm 3: High-Level Server Logic — One-to-One Chat (Feature 2)
#
# Create a TCP server socket and bind it to an IP address and port
# Start listening for incoming client connections
# Initialize an empty dictionary to store each client's username and socket
#
# while server is running:
#     Accept a new client connection
#     Request and receive the client's username
#     Add the username–socket pair to the dictionary
#     Start a new thread to handle communication with that client
#
#     Client Handler (in each thread):
#         while the client is connected:
#             Wait to receive a message from the client
#
#             if message starts with @target:
#                 Extract the target username and message text
#
#                 if target username exists in the client dictionary:
#                     Send the message only to that specific target client
#                 else:
#                     Inform the sender that the target user was not found
#
#             else:
#                 Inform the sender to use the correct format (@username message)
#
#         When the client disconnects, remove it from the dictionary
