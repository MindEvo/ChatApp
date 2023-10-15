######################
##  LIBRARIES USED  ##
######################
import socket
import sys
import select
import threading
import struct

exitFlag = threading.Event()
connection_id = 0
active_connections = {}
sockets = []
lock = threading.Lock()

##########################
##      METHODS         ##
##########################

def user_interface():
    print("Welcome to the Chat Application!")
    print("Type 'help' for available commands.")

    while not exitFlag.is_set():
        command = input("> ")
        handle_user_command(command)

def handle_user_command(command):
    if command == 'help':
        display_help()
    elif command == 'myip':
        print("> Your IP address is:", get_ip())
    elif command == 'myport':
        print("> Listening on port:", listening_port)
    elif command.startswith('connect'):
        handle_connect_command(command)
    elif command == 'list':
        list_connections()
    elif command.startswith('terminate'):
        handle_terminate_command(command)
    elif command.startswith('send'):
        handle_send_command(command)
    elif command == 'exit':
        handle_exit_command()
    else:
        print("Invalid command. Type 'help' for available commands.")

def display_help():
    print("Available commands:")
    print("help - Display help information")
    print("myip - Display your IP address")
    print("myport - Display the port on which you're listening")
    print("connect <destination> <port> - Connect to another peer")
    print("list - List all active connections")
    print("terminate <connection_id> - Terminate a connection")
    print("send <connection_id> <message> - Send a message to a connection")
    print("exit - Close all connections and exit the application")

def handle_connect_command(command):
    parts = command.split()
    if len(parts) != 3:
        print("Invalid command. Usage: connect <destination> <port>")
    else:
        destination = parts[1]
        port = int(parts[2])
        connect_to_peer(destination, port)

def handle_terminate_command(command):
    parts = command.split()
    if len(parts) != 2:
        print("Invalid command. Usage: terminate <connection_id>")
    else:
        connection_id = int(parts[1])
        terminate_connection(connection_id)

def handle_send_command(command):
    parts = command.split(' ', 2)
    if len(parts) != 3:
        print("Invalid command. Usage: send <connection_id> <message>")
    else:
        connection_id = int(parts[1])
        message = parts[2]
        send_message(connection_id, message)

def handle_exit_command():
    exitFlag.set()
    close_all_connections()

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print("Error getting IP address:", str(e))
        return "Unknown"

def create_listener(port):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(('0.0.0.0', port))
    listener.listen(5)
    return listener

def connect_to_peer(destination, port):
    global connection_id
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((destination, port))
        with lock:
            connection_id += 1
            active_connections[connection_id] = s
            sockets.append(s)
        print(f"> Connection to peer {destination} is established with connection ID: {connection_id}")
    except Exception as e:
        print("Connection error:", str(e))

def list_connections():
    with lock:
        print("> ID: \tIP address: \tPort:")
        for connection in active_connections:
            print(f"> {connection} \t{active_connections[connection].getpeername()[0]} \t{active_connections[connection].getpeername()[1]}")

def terminate_connection(connection_id):
    with lock:
        if connection_id in active_connections:
            try:
                s = active_connections[connection_id]
                s.close()
                if s in sockets:
                    sockets.remove(s)
                del active_connections[connection_id]
            except Exception as e:
                print("Error closing connection:", str(e))
                
def send_message(connection_id, message):
    with lock:
        if connection_id in active_connections:
            try:
                active_connections[connection_id].send(message.encode('utf-8'))
                print("> Message sent")
            except:
                print(f"> Error sending message to: {active_connections[connection_id].getpeername()[0]}")

def close_all_connections():
    with lock:
        for _, conn in active_connections.items():
            conn.close()
        active_connections.clear()
        sockets.clear()

def handle_incoming_connections(listener):
    while not exitFlag.is_set():
        global connection_id
        try:
            read_sockets, _, _ = select.select(sockets, [], [], 1)
            for sock in read_sockets:
                if sock == listener:
                    new_socket, _ = listener.accept()
                    with lock:
                        connection_id += 1
                        active_connections[connection_id] = new_socket
                        sockets.append(new_socket)
                    print(f"Connection to peer {new_socket.getpeername()[0]} is established with ID: {connection_id}")
        except Exception as e:
            print("Error accepting connection:", str(e))

def handle_incoming_messages(listener):
    while not exitFlag.is_set():
        try:
            read_sockets, _, _ = select.select(sockets, [], [], 1)
            for sock in read_sockets:
                if sock != listener:
                    data = sock.recv(1024).decode()
                    if data:
                        print(f"From {sock.getpeername()[0]}: {data}")
                    else:
                        with lock:
                            for id, conn in active_connections.items():
                                if conn == sock:
                                    del active_connections[id]
                                    break
                            if sock in sockets:
                                sockets.remove(sock)
                            sock.close()
        except Exception as e:
            print("Error accepting incoming message:", str(e))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ./chat <port>")
        sys.exit(1)

    listening_port = int(sys.argv[1])
    listener = create_listener(listening_port)
    sockets.append(listener)

    user_interface_thread = threading.Thread(target=user_interface)
    user_interface_thread.start()

    incoming_connections_thread = threading.Thread(target=handle_incoming_connections, args=(listener,))
    incoming_connections_thread.start()

    incoming_messages_thread = threading.Thread(target=handle_incoming_messages, args=(listener,))
    incoming_messages_thread.start()

    user_interface_thread.join()
    incoming_connections_thread.join()
    incoming_messages_thread.join()
