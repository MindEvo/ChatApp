# Simple Chat Application

A basic peer-to-peer chat application built using Python's `socket`, `select`, and `threading` libraries.

## Features

- Establish connections with multiple peers.
- Send and receive messages in real-time.
- List all active connections.
- Terminate individual connections.
- Graceful shutdown of the application.

## Requirements

- Python 3.x

## Usage

1. **Starting the Application**:
    ```
    python chat.py <port>
    ```

    Replace `<port>` with the port number you want the application to listen on.

2. **Available Commands**:
    - `help`: Display available commands.
    - `myip`: Display your IP address.
    - `myport`: Display the port on which you're listening.
    - `connect <destination> <port>`: Connect to another peer.
    - `list`: List all active connections.
    - `terminate <connection_id>`: Terminate a specific connection.
    - `send <connection_id> <message>`: Send a message to a specific connection.
    - `exit`: Close all connections and exit the application.

3. ## Limitations

- The application assumes a stable network connection.
- Messages are sent in plain text without encryption.

4. ## Bugs

When terminating a connection, two bugs are displayed in the terminal:
	-  Error accepting connection: file descriptor cannot be a negative integer (-1)
	-  Error accepting incoming message: [WinError 10038] An operation was attempted on something that is not a socket
Despite these issues, connections still get terminated and are verified when calling the list command. 

When exiting the program while having active connections the following bug is displayed:
	- Error accepting incoming message: [WinError 10038] An operation was attempted on something that is not a socket
Despite this bug the program will still exit and return the user to the command line.