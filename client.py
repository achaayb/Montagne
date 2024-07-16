import json
import logging
import socket
import struct
from typing import Any

from constants import (B_CONNECT, B_DISCONNECT, B_EVENT_TRIGGER, B_EVENT_RESPONSE,
                       B_CONNECTED, B_DISCONNECTED, B_REFUSED)

logging.basicConfig(level=logging.INFO)


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
        intro_payload = self._create_payload(B_EVENT_TRIGGER, payload_json)
        self.socket.sendall(intro_payload)
        

    def disconnect(self) -> bool:
        if self.socket:
            self.socket.close()
            return True
        return False

    def _create_payload(self, packet_type, body) -> bytes:
        body_bytes = body.encode("utf-8")
        body_len = len(body_bytes)
        header = struct.pack("!HI", packet_type, body_len)
        payload = header + body_bytes
        return payload

if __name__ == "__main__":
    client = MontagneClient("localhost", 5000)
    client.connect()

    client.send_event("kaka", [1,2,3], {"sda": "asdas"})

    try:
        while True:
            foo = int(input("foo: "))
            if foo == 1:
                client.send_event("kaka", [1,2,3], {"sda": "asdas"})
            elif foo == 2:
                client.send_event("kdasdsaka", [1,2,3], {"sda": "asdas"})
            #logging.info(response)
    except KeyboardInterrupt:
        logging.info("Manual exit")
    finally:
        client.disconnect()