import json
import socket
import struct
from threading import Thread
import pickle

class MontagneServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.connections = []
        self.tasks = {}

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(5)
        print("# ᨒ↟ ⋆｡°")
        print(f"# Montagne server running @ {self.host}:{self.port}")
        while True:
            client_socket, client_address = self.server.accept()
            print(f"# New connection from {client_address}")
            client_handler = Thread(
                target=self._connection_handler,
                args=(client_socket, client_address),  # noqa
            )
            client_handler.start()
            self.connections.append(client_socket)

    def task(self, tag=None):
        def decorator(func):
            self.tasks[tag] = func
            return func
        return decorator

    def _connection_handler(self, client_socket, client_address):
        while True:
            intro_payload = client_socket.recv(13)
            p_type, b_len = struct.unpack("!5sQ", intro_payload)
            if p_type != b"EVENT":
                continue
            payload_body = client_socket.recv(b_len)
            payload_json = json.loads(payload_body)
            task_tag = payload_json.get("tag", None)
            task_args = payload_json.get("args", [])
            task_kwargs = payload_json.get("kwargs", {})
            task = self.tasks.get(task_tag, None)
            if not task:
                continue
            result = task(client_socket, client_address, *task_args, **task_kwargs)
            result_payload = self._create_payload(b"RESLT", result)
            client_socket.sendall(result_payload)
            print(f"# Sent to {client_address}")

    def _create_payload(self, packet_type, body) -> bytes:
        body_bytes = pickle.dumps(body)
        body_len = len(body_bytes)
        header = struct.pack("!5sQ", packet_type, body_len)
        payload = header + body_bytes
        return payload
    
    def close(self):
        self.server.close()



if __name__ == "__main__":
    montagne_app = MontagneServer("localhost", 5001)

    @montagne_app.task("exc")
    def foo(socket, client_address, *args, **kwargs):
        return Exception

    try:
        montagne_app.run()
    except KeyboardInterrupt:
        pass
    finally:    
        montagne_app.close()