import logging
import socket
import struct

from constants import (B_AUTHENTICATE, B_MESSAGE, STR_AUTH_FAILURE,
                       STR_AUTH_SUCCESS)

logging.basicConfig(level=logging.INFO)


class Client:
    def __init__(self, host, port, username="username", password="password"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            packet = self._create_packet(
                B_AUTHENTICATE, f"{self.username}:{self.password}"
            )
            self.socket.sendall(packet)
            response = self.socket.recv(24)
            if response == STR_AUTH_SUCCESS.encode("utf-8"):
                logging.info("Authentication success")
            elif response == STR_AUTH_FAILURE.encode("utf-8"):
                logging.info("Authentication failure")

        except ConnectionRefusedError:
            logging.info("Connection refused")
        except Exception as e:
            logging.info(f"Error connecting to server: {e}")

    def _create_packet(self, packet_type, payload):
        payload_bytes = payload.encode("utf-8")
        payload_len = len(payload_bytes)
        # Is not actually a header but
        # the server will read first bytes then decide
        # if he wants to keep reading.. to avoid spam x)
        header = struct.pack("!BI", packet_type, payload_len)
        packet = header + payload_bytes
        return packet

    def send(self, payload):
        packet = self._create_packet(B_MESSAGE, payload)
        self.socket.sendall(packet)
        response = self.socket.recv(4096).decode("utf-8")
        return response

    def disconnect(self):
        if self.socket:
            self.socket.close()
            logging.info("Disconnected from server")


if __name__ == "__main__":
    client = Client("localhost", 5000)
    client.connect()

    try:
        while True:
            message = input("message: ")
            response = client.send(message)
            logging.info(response)
    except KeyboardInterrupt:
        logging.info("Manual exit")
    finally:
        client.disconnect()