import socket
import threading

def handle_client(client_socket):
    while True:
        message = client_socket.recv(1024).decode('utf-8')
        if message == 'exit':
            print('Client disconnected')
            break
        print(f"Received: {message}")
    client_socket.close()

def start_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', port))
    server.listen()
    print(f"Server is listening on port {port}")

    while True:
        client_socket, address = server.accept()
        print(f"Accepted connection from {address}")
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    start_server(4322)
