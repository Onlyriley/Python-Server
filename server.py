from collections import UserList
import socket
import threading
import time

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '/disconnect'




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# When a user connects it will ask them for a username
# This the username they selected and their IP are passed here
# username and address are bound together
# * only the username is shown to the other clients *
# In the future logging can be enabled so the IP of each client is recorded along with each message
# Stored in the following format
# [addr, username]
def username_config():
    global userkeys
    userkeys = {}



# This is the chat thread
# This makes sure that all clients recieve messages that other clients send
# There are many redundant variables and I'm not even entirely sure why this works, but it does and it does it well
def chat_thread():
    global msglist
    global msgcount
    global feedback
    global msg_update
    msglist = []
    msgcount = 0
    feedback = []
    msg_update = False
    while True:
        chat_loop = False
        if msglist.__len__() != msgcount:
            while chat_loop == False:
                msg_update = True
                if feedback.__len__() > connections:
                    pass
                if feedback.__len__() == connections: chat_loop = True
            msgcount += 1
            feedback = []
            msg_update = False


# Currently sends back messages that the server recieves
# Flaws, it only sends the message back to one client

# Updated to work with chat_thread to send messages to each of the clients and making sure messages are updated (Not working rn) 
def handle_inbound(conn, addr):
    while True:
        handle_loop = False
        if msg_update == True:
            conn.send(f"{msglist[msgcount]}".encode(FORMAT))
            feedback.append(True)
        while handle_loop == False:
            if feedback.__len__() == 0: handle_loop = True


def handle_client(conn, addr):
    print(f"{addr} CONNECTED")
    connected = True
    global connections
    connections =+ 1
    connection_auth = False


    # Before moving to normal chat we recieve the client's username
    while connection_auth == False:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            userkeys[addr] = msg
            print(f"{addr} has connected as {userkeys[addr]}")
            msglist.append(f"{userkeys[addr]} has connected")
            connection_auth = True


    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            msglist.append(f"{userkeys[addr]}: {msg}")
            print(f"{userkeys[addr]}: {msg}")
            #conn.send(f"{addr}: {msg}".encode(FORMAT))
            #this was the original method of the chat thread, only works with 1 client
    conn.close()
    print(f"CONNECTION CLOSED @ {addr}")
    connections =- 1


def start():
    server.listen()
    print("SERVER ({}) LISTENING ON PORT {}".format(socket.gethostbyname(socket.gethostname()), PORT))
    global connections
    connections = 0

    # Starts the chat thread
    chat_thread_thread = threading.Thread(target=chat_thread)
    chat_thread_thread.start()

    # Starts the username thread
    # This is very lightweight, does not loop
    username_thread = threading.Thread(target=username_config)
    username_thread.start()

    # Starts the main loop
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread2 = threading.Thread(target=handle_inbound, args=(conn,addr))
        thread.start()
        thread2.start()
        print(f"{connections} ACTIVE CONNECTIONS")

print("STARTING SERVER...")
if __name__ == "__main__":
    start()