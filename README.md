# Montagne

Montagne is a python tcp socket client server framework

## Installation

No external dependencies are required. Simply copy `client.py` `server.py` and `constants.py` files into your project.

## Usage

### Basic Client Example

```python
from client import MontagneClient

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
```

### Basic Server Example

```python
from server import MontagneServer

if __name__ == "__main__":
    montagne_app = MontagneServer("localhost", 5000)

    @montagne_app.event("kaka")
    def foo(socket, *args, **kwargs):
        socket.sendall("hi".encode("utf-8"))

    try:
        montagne_app.run()
    except KeyboardInterrupt:
        montagne_app.close()
```


### Run with howver you usually run your python scripts with

```bash
python3 <your_app>.py
```