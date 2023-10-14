import socket
import sys
import select
import threading

# A global dictionary to hold active connections. The keys are connection IDs (integers),
# and the values are dictionaries containing the 'socket' object and 'address' tuple.
connections = {}
next_connection_id = 1  # The ID to be assigned to the next new connection

# Function to display the user interface and handle user commands
def user_interface():
    print("Welcome to the Chat Application!")
    print("Type 'help' for available commands.")

    while True:
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
                _, destination, port = command.split()
                connect_to_peer(destination, int(port))
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

# Function to receive messages
def receive_messages(connection_id, client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if not message:
                break
            print(f"Message received from connection {connection_id}: {message}")
    except Exception as e:
        print(f"Error receiving message: {str(e)}")
    finally:
        client_socket.close()

# Function to handle incoming connections
def handle_incoming_connections(server_socket):
    global connections, next_connection_id
    
    while True:
        client_socket, client_address = server_socket.accept()
        print('The ip is',get_ip())
        connections[next_connection_id] = {'socket': client_socket, 'address': client_address}
        print(f"New connection from {client_address} with ID {next_connection_id}")
         # Start a new thread to receive messages from this connection
        threading.Thread(target=receive_messages, args=(next_connection_id, client_socket)).start()
        
        next_connection_id += 1

# Function to establish a connection to another peer
def connect_to_peer(destination, port):
    # Implement this function to create a socket and connect to the specified destination
    global connections, next_connection_id  # Declare as global so we can modify them
    try:
        peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        peer_socket.connect((destination, port))
        connections[next_connection_id] = {'socket': peer_socket, 'address': (destination, port)}
        print(f"Connected to {destination} on port {port} with connection ID {next_connection_id}.")
        next_connection_id += 1  # Increment the connection ID for the next connection
    except Exception as e:
        print(f"Failed to connect to {destination}:{port} - {str(e)}")
    pass

# Function to list all active connections
def list_connections():
    # Implement this function to display a numbered list of active connections
    global connections  # Declare 'connections' as global so we can modify it
    if not connections:
        print("No active connections.")
    else:
        print("Active connections:")
        for connection_id, info in connections.items():
            print(f"{connection_id}: {info['address'][0]} {info['address'][1]}")
    pass

# Function to terminate a connection
def terminate_connection(connection_id):
    # Implement this function to close the specified connection'
    global connections
    
    if connection_id not in connections:
        print(f"No connection found with ID {connection_id}")
        return

    connection_info = connections[connection_id]
    client_socket = connection_info['socket']

    try:
        client_socket.shutdown(socket.SHUT_RDWR)
        client_socket.close()
        print(f"Connection {connection_id} terminated")
    except Exception as e:
        print(f"Error terminating connection {connection_id}: {str(e)}")
    
    # Remove the connection from the connections dictionary
    del connections[connection_id]
    pass

# Function to send a message to a connection
def send_message(connection_id, message):
    # Implement this function to send the message to the specified connection
    global connections
    
    if connection_id not in connections:
        print(f"No connection found with ID {connection_id}")
        return

    connection_info = connections[connection_id]
    client_socket = connection_info['socket']
    try:
        client_socket.sendall(message.encode())
        print(f"Message sent to {connection_id}")
    except Exception as e:
        print(f"Failed to send message: {str(e)}")

    pass

# Function to close all connections
def close_all_connections():
    # Implement this function to close all active connections
    global connections
    
    # If there are no active connections
    if not connections:
        print("No active connections to close.")
        return
    
    for connection_id, connection_info in list(connections.items()):
        client_socket = connection_info['socket']
        
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
            print(f"Connection {connection_id} closed.")
        except Exception as e:
            print(f"Error closing connection {connection_id}: {str(e)}")
    
    # Clear the connections dictionary
    connections.clear()
    print("All connections closed.")
    pass

# Entry point of the program
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python app.py <port>")
        sys.exit(1)

    listening_port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', listening_port))
    server_socket.listen(5)

    # Create a new thread to handle incoming connections
    threading.Thread(target=handle_incoming_connections, args=(server_socket,)).start()

    print(f"Listening for incoming connections on port {listening_port}")

    # Here is where the user interface function is called to handle user inputs and commands
    user_interface()
