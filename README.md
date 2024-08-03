# Montagne

**Experimental TCP Client-Server Project**: This project demonstrates a TCP client-server setup where the client triggers tasks (functions) on the server. The server processes these tasks and sends back a pickled response, which the client can then unpickle for further use.

### Code Overview

- **MontagneClient**:
  - `connect()`: Connects to the socket server.
  - `send_event(tag, args, kwargs)`: Sends an event with a specified tag and optional arguments and keyword arguments.
  - `_create_payload(packet_type, body)`: Creates a payload with a header and body.
  - `disconnect()`: Closes the connection to the server.

- **MontagneServer**:
  - `run()`: Starts the server and listens for client connections.
  - `task(tag)`: Decorator to register a task for a specific tag.
  - `_connection_handler(client_socket, client_address)`: Handles incoming connections and processes tasks.
  - `_create_payload(packet_type, body)`: Creates a payload with a header and body.
  - `close()`: Closes the server.

  **Flow**:
  - Client connects to the socket server.
  - Server accepts the client connection and handles the connection in a separate thread.
  - Client creates a payload using `._create_payload(b"EVENT", body)` and sends it using `.send_event(tag, args, kwargs)`.
  - Server always attempts to read 13 bytes (value from :`struct.calcsize("!5sQ")`).
  - The first 5 bytes represent the event scope, which is either `EVENT` or `RESLT`.
  - The following 8 bytes represent an unsigned integer indicating the body's length.
  - Server determines the event controller by tag.
  - Server Pickles the controller response and creates a payload using `._create_payload(b"RESLT", body)`.
  - Meanwhile, the client blocks execution until 13 bytes are received.
  - Client determines the body length n, attempts to receive n bytes (body), and unpickles it.
  - `.send_event(tag, args, kwargs)` returns the unpickled result.

### Example

To test the client-server communication, run the server and client in separate terminals and interact with the client by sending events. This should be self-explanatory in the `__main__` block.

### License

Experimental project. Use it as you please.
