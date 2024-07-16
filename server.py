import json
import logging
import socket
import struct
from threading import Thread

from constants import (B_ACCEPTED, B_CONNECT, B_DISCONNECT, B_EVENT_DOESNT_EXIST, B_EVENT_TRIGGER,
                       B_CONNECTED, B_DISCONNECTED, B_REFUSED)

logging.basicConfig(level=logging.INFO)


class MontagneServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.connections = []
        self.events = {}

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        logging.info(f"Montagne server listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server.accept()
            logging.info(f"Client {client_address} connected")
            # Creates a thread per connection.
            client_handler = Thread(
                target=self._connection_handler,
                args=(client_socket, client_address),  # noqa
            )
            client_handler.start()
            self.connections.append(client_socket)

    def event(self, tag=None):
        def decorator(func):
            self.events[tag] = func
            return func
        return decorator

    def _connection_handler(self, client_socket, client_address):
        while True:
            intro_payload = client_socket.recv(6)
            p_type, b_len = struct.unpack("!HI", intro_payload)
            if p_type == B_EVENT_TRIGGER:
                payload_body = client_socket.recv(b_len)
                payload_json = json.loads(payload_body)
                event_tag = payload_json.get("tag", None)
                event_args = payload_json.get("args", [])
                event_kwargs = payload_json.get("kwargs", {})
                event = self.events.get(event_tag, None)
                if not event:
                    event_not_found_payload = self._create_payload(B_EVENT_DOESNT_EXIST, "")
                    client_socket.sendall(event_not_found_payload)
                    logging.info(f"Event {event_tag} not found")
                else:
                    event(client_socket, *event_args, **event_kwargs)
                    print(f"Event {event_tag} done")
            else:
                continue


    def _create_payload(self, packet_type, body):
        body_bytes = body.encode("utf-8")
        body_len = len(body_bytes)
        header = struct.pack("!BI", packet_type, body_len)
        payload = header + body_bytes
        return payload
    
    def close(self):
        self.server.close()



if __name__ == "__main__":
    montagne_app = MontagneServer("localhost", 5000)

    @montagne_app.event("kaka")
    def foo(socket, *args, **kwargs):
        socket.sendall("hi".encode("utf-8"))

    try:
        montagne_app.run()
    except KeyboardInterrupt:
        montagne_app.close()