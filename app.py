import socket
import sys
import select
import threading

exitFlag = False  # Global flag to signal threads to exit

connection_id = 0

# Create a dictionary to store information about active connections
active_connections = {}

# Create a list of sockets to be monitored by select
sockets = []

# Function to display the user interface and handle user commands
def user_interface():
    global exitFlag
    print("Welcome to the Chat Application!")
    print("Type 'help' for available commands.")

    while not exitFlag:  # Check the exitFlag
        command = input("> ")
        if command == 'help':
            # Display command help information
            print("Available commands:")
            print("help - Display help information")
            print("myip - Display your IP address")
            print("myport - Display the port on which you're listening")
            print("connect <destination> <port> - Connect to another peer")
            print("list - List all active connections")
            print("terminate <connection_id> - Terminate a connection")
            print("send <connection_id> <message> - Send a message to a connection")
            print("exit - Close all connections and exit the application")
        elif command == 'myip':
            # Display the local IP address
            print("Your IP address is:", get_ip())
        elif command == 'myport':
            # Display the listening port
            print("Listening on port:", listening_port)
        elif command.startswith('connect'):
            # Handle the connect command
            # Extract destination IP and port from the command
            parts = command.split()
            if len(parts) != 3:
                print("Invalid command. Usage: connect <destination> <port>")
            else:
                destination = parts[1]
                port = int(parts[2])
                connect_to_peer(destination, port)
        elif command == 'list':
            # List all active connections
            list_connections()
        elif command.startswith('terminate'):
            # Terminate a connection
            parts = command.split()
            if len(parts) != 2:
                print("Invalid command. Usage: terminate <connection_id>")
            else:
                connection_id = int(parts[1])
                terminate_connection(connection_id)
        elif command.startswith('send'):
            # Send a message to a connection
            parts = command.split(' ', 2)
            if len(parts) != 3:
                print("Invalid command. Usage: send <connection_id> <message>")
            else:
                connection_id = int(parts[1])
                message = parts[2]
                send_message(connection_id, message)
        elif command == 'exit':
            exitFlag = True
            # Close all connections and exit
            close_all_connections()
            break
        else:
            print("Invalid command. Type 'help' for available commands.")

# Function to get the local IP address
def get_ip():
    # This function depends on your platform and network configuration
    # You may need to adapt it to retrieve the correct local IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))  # Google's public DNS server
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print("Error getting IP address:", str(e))
        return "Unknown"

# Function to create a socket for listening
def create_listener(port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', port))  # Bind to all available network interfaces
    listener.listen(5)
    return listener

# Function to establish a connection to another peer
def connect_to_peer(destination, port):
    global connection_id
    try:
        # Create a socket for the client
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)  # Set a timeout of 10 seconds for the connection attempt

        # Connect to the destination (another peer) using the specified IP and port
        s.connect((destination, port))

        # Increment the connection ID counter and assign a unique ID to this connection
        connection_id += 1

        # Store connection information in the active_connections dictionary
        active_connections[connection_id] = s

        # Add the new socket to the list of sockets to be monitored
        sockets.append(s)

        # Notify both peers that the connection is established
        s.send("Connection established.".encode('utf-8'))
        print(f"Connected to {destination}:{port} with connection ID {connection_id}")

    except Exception as e:
        print("Connection error:", str(e))
    

# Function to list all active connections
def list_connections():
    print("id:  IP address:     Port No.")
    for connection in active_connections:
        print(f"{connection} , {active_connections[connection].getpeername()}")

# Function to terminate a connection
def terminate_connection(connection_id):
    # Implement this function to close the specified connection
    pass

# Function to send a message to a connection
def send_message(connection_id, message):
    # Implement this function to send the message to the specified connection
    pass

# Function to close all connections
def close_all_connections():
    # Implement this function to close all active connections
    pass


# Function to handle incoming connections
def handle_incoming_connections(listener):
    while not exitFlag:  # Check the exitFlag
        global connection_id
        try:
            read_sockets, _, _ = select.select([listener], [], [], 1)
            for sock in read_sockets:
                if sock == listener:
                    # New connection, accept it
                    new_socket, _ = listener.accept()
                    sockets.append(new_socket)
                    connection_id += 1
                    active_connections[connection_id] = new_socket

                    # Notify that a new connection is established
                    print("New connection:", new_socket.getpeername())

        except Exception as e:
            print("Error accepting connections:"), str(e)


# Entry point of the program
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./chat <port>")
        sys.exit(1)

    listening_port = int(sys.argv[1])

    listener = create_listener(listening_port)
    sockets.append(listener)

    # Start the user interface in a separate thread
    user_interface_thread = threading.Thread(target=user_interface)
    user_interface_thread.start()

    # Start the handle_incoming_connections function in another thread
    incoming_connections_thread = threading.Thread(target=handle_incoming_connections, args=(listener,))
    incoming_connections_thread.start()

    user_interface_thread.join()
    incoming_connections_thread.join()
