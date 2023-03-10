import socket
import threading
import sys
from time import sleep
from random import randint

HEADER = 64

HOST = socket.getaddrinfo(socket.gethostname(), None)[2][4][0]
PORT = 5050

connections = []
new_snakes = []
apples = [[randint(5, 110)*10, randint(5, 70)*10] for _ in range(10)]


def handle_client(conn, addr):
    global new_snakes, score
    nickname = receive(conn)
    data = receive(conn)

    threading.current_thread().nickname = nickname
    threading.current_thread().conn = conn

    # sending all players new player joined
    send_to_all(data, conn)
    # sending all snakes
    new_snakes = []
    for c in connections:
        if c != conn:
            send(c, "[ASK_POS]")
            sleep(0.5)
            send(conn, new_snakes[-1])
    # sending all apples
    for a in apples:
        send(c, f"[APPLE+]|{','.join(map(str,a))}")

    send_to_all(f"[CHAT]|{nickname} joined!")

    while 1:
        data = receive(conn)
        prefix = data.split("|")[0]
        if prefix == "[NEW]":
            new_snakes.append(data)
        elif prefix == "[APPLE-]":
            apples.remove(list(map(int, data.split("|")[1].split(","))))
            send_to_all(data, conn)
            apples.append([randint(5, 100)*10, randint(5, 70)*10])
            send_to_all(f"[APPLE+]|{','.join(map(str,apples[-1]))}")
        elif prefix == "[CHAT]":
            send_to_all(data)
        else:
            send_to_all(data, conn)


def handle_disconnect(args):
    errors = [ConnectionResetError,
              ConnectionAbortedError,
              ConnectionError,
              ConnectionRefusedError]
    nickname = threading.current_thread().nickname
    if args.exc_type in errors:
        print(
            f"Connection lost with client {nickname}. Err: {args.exc_type.__name__}")
        connections.remove(threading.current_thread().conn)
        send_to_all(f"[CHAT]|{nickname} left")
        send_to_all(f"[LEFT]|{nickname}")
    else:
        sys.__excepthook__(
            args.exc_type, args.exc_value, args.exc_traceback)


def send_to_all(msg, excluded=None):
    for c in connections:
        if c != excluded:
            send(c, msg)


def receive(conn):
    msg_len = conn.recv(HEADER)
    msg_len = int(msg_len.decode())
    msg = conn.recv(msg_len).decode()
    return msg


def send(conn, msg):
    msg_len = str(len(msg.encode()))
    msg_len = msg_len.encode() + b" "*(HEADER-len(msg_len))
    conn.send(msg_len)
    conn.send(msg.encode())


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((HOST, PORT))
        sock.setblocking(True)
        sock.listen()
        print(f"Server is listening on {(HOST,PORT)}")
        while True:
            conn, addr = sock.accept()
            print(f"New client connected from {addr}")
            connections.append(conn)
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()


if __name__ == "__main__":
    threading.excepthook = handle_disconnect
    main()
