import socket
import time
import threading



HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '/disconnect'
SERVER = "45.79.202.153"

def define_ip(SERVER):
    print("Enter IP to connect to, or press enter to connect automatically:")
    define_ip_input = input("")
    if define_ip_input.__len__() != 0:
        SERVER = define_ip_input.strip()
    return SERVER
ADDR = (define_ip(SERVER), PORT)


def connect():
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
    except ConnectionRefusedError:
        print("Connection error: retrying...")
        time.sleep(3)
        connect()
    print("Connected to server")
    print("Please enter your username:")
    username = input("")
    msg = username
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)



def send():
    userinput = input("")
    msg = userinput
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)

    
def recieve():
    print(client.recv(2048).decode(FORMAT))


def start():
    connect()
    while True:
        thread = threading.Thread(target = send)
        thread2 = threading.Thread(target = recieve)
        thread.start()
        thread2.start()

if __name__ == "__main__":
    start()