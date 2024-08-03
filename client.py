import json
import socket
import struct
from typing import Any
import pickle


class MontagneClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))

    def send_event(self, tag: str, args: list[Any] = None, kwargs: dict[str: Any] = None) -> Any:
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        payload_dict = {
            "tag": tag,
            "args": args,
            "kwargs": kwargs
        }
        payload_json = json.dumps(payload_dict)
        payload = self._create_payload(b"EVENT", payload_json)
        self.socket.sendall(payload)

        intro_payload = self.socket.recv(13)
        r_type, b_len = struct.unpack("!5sQ", intro_payload)
        if r_type != b"RESLT":
            return
        result_body = self.socket.recv(b_len)
        result = pickle.loads(result_body)
        return result
        
    def _create_payload(self, packet_type, body) -> bytes:
        body_bytes = body.encode("utf-8")
        body_len = len(body_bytes)
        header = struct.pack("!5sQ", packet_type, body_len)
        payload = header + body_bytes
        return payload

    def disconnect(self) -> bool:
        if self.socket:
            self.socket.close()
            return True
        return False


if __name__ == "__main__":
    client = MontagneClient("localhost", 5001)
    client.connect()

    try:
        while True:
            foo = input("foo: ")
            if foo == "a":
                result = client.send_event("exc", [1,2,3], {"sda": "asdas"})
                print(type(result))
            else:
                continue
    except KeyboardInterrupt:
        pass
    finally:
        client.disconnect()