import socket
import logging
import struct
import sqlite3
from threading import Thread
from queue import Queue
from constants import B_AUTHENTICATE, STR_AUTH_FAILURE, STR_AUTH_SUCCESS, LIST_DEFAULT_CREDENTIALS

logging.basicConfig(level=logging.INFO)


class AuthManager:
    def __init__(self, credentials: list[tuple[str, str]] | None = None):
        self.credentials = credentials if credentials else LIST_DEFAULT_CREDENTIALS

    def check_credentials(self, username, password):
        if (username, password) in self.credentials:
            return True
        return False

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.connections = []
        self.auth_manager = AuthManager()

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        logging.info(f"SQLite server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server.accept()
            logging.info(f"Accepted connection from {client_address}")
            # First 5 bytes are always packet type.
            # this protects against spam...
            introduction_packet = client_socket.recv(5)
            # B unsigned char
            # I unsigned int
            packet_type, next_len = struct.unpack("!BI", introduction_packet)
            if packet_type == B_AUTHENTICATE:
                logging.info(f"Auth packet received from {client_address}")
                credentials_packet = client_socket.recv(next_len)
                username, password = credentials_packet.decode("utf-8").split(":")
                if self.auth_manager.check_credentials(username, password):
                    logging.info(f"Auth accepted from {client_address}")
                    client_socket.sendall(STR_AUTH_SUCCESS.encode("utf-8"))
                else:
                    logging.info(f"Auth denied from {client_address}")
                    client_socket.sendall(STR_AUTH_FAILURE.encode("utf-8"))
                    continue
            # Creates a thread per connection.
            client_handler = Thread(target=self._handle_connection, args=(client_socket, client_address))
            client_handler.start()
            self.connections.append(client_socket)
    
    def close(self):
        self.server.close()

    def _close_connection(self, client_socket):
        client_socket.close()


    def _handle_connection(self, client_socket, client_address):
        try:
            while True:
                request = client_socket.recv(4096).decode('utf-8')
                # If connection is closed .recv returns b''
                if not request:
                    break
                
                client_socket.sendall(request.encode('utf-8'))
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            self._close_connection(client_socket)
            logging.info(f"Connection Disconnected {client_address}")

if __name__ == "__main__":
    server = Server('localhost', 5000)
    server.start()
    server.close()