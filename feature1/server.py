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
