# Algorithm 1 High-level Server Logic for broadcast feature

# 1: Create a TCP server socket and bind it to an IP address and port
# 2: Start listening for incoming client connections
# 3: Initialize an empty list to store connected clients

# 4: while server is running do
# 5:    Accept a new client connection
# 6:    Add the client to the list of active clients
# 7:    Start a new thread to handle communication with that client
# 8: end while

# 9: Client Handler (in each thread):
# 10: Continuously receive messages from the assigned client
# 11: For each received message, forward it to all other connected clients
# 12: If the client disconnects, close the connection and remove it from the list
