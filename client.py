import socket

def start_client(port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('127.0.0.1', port))

    while True:
        message = input("Enter message (type 'exit' to disconnect): ")
        client.send(message.encode('utf-8'))
        if message == 'exit':
            break

    client.close()

if __name__ == "__main__":
    start_client(4322)
