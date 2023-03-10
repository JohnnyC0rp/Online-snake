import socket
import sys

HEADER = 64


def handle_disconnect(args):
    errors = [ConnectionResetError,
              ConnectionAbortedError,
              ConnectionError,
              ConnectionRefusedError]
    if args.exc_type in errors:
        print(
            f"Connection lost with remote server. Err: {args.exc_type.__name__}")
        disconnected()
    else:
        sys.__excepthook__(
            args.exc_type, args.exc_value, args.exc_traceback)


def connect(addr: tuple) -> str:
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Connecting...")
    try:
        conn.connect(addr)
    except Exception as e:
        print("Can't connect to the remote server.")
        print("Error: ", e)
        exit()
    print(f"Connected to server at {addr}")

    return conn


def handshake(nickname, mySnake):
    send(nickname)
    send(str(mySnake))


def receive():
    msg_len = int(conn.recv(HEADER).decode())
    msg = conn.recv(msg_len).decode()
    return msg.strip()


def send(msg):
    msg_len = str(len(msg.encode()))
    msg_len = msg_len.encode() + b" "*(HEADER-len(msg_len))
    conn.send(msg_len)
    conn.send(msg.encode())


def disconnected():
    print("[CONNECTION LOST]")
    _ = input("Your feedback is incredibly important:")
