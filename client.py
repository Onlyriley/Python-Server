import socket
import time
import threading
import globals
import sys
# Using pisimploeGUI for GUI for now
# Moving GUI over to clientgui.py for the sake of saving space and confusion here
import clientgui

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '/disconnect'
SERVER = "45.79.202.153"

wsys = sys.stdout

def define_ip(SERVER):
    # V This is for dev only
    #print("Press enter to connect or manually enter IP:")
    #define_ip_input = input("")
    #if define_ip_input.__len__() != 0:
    #    SERVER = define_ip_input.strip()
    return SERVER
ADDR = (define_ip(SERVER), PORT)

# This handles connecting as well as sending the username
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
    #username = input("")
    username = clientgui.gui_login()
    msg = username
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)



def send():
    global connected
    global send_list
    connected = True
    global userinput
    send_list = []
    while True:
        for item in globals.recieve_list:
            if item not in send_list:
                msg = item
                message = msg.encode(FORMAT)
                msg_length = len(message)
                send_length = str(msg_length).encode(FORMAT)
                send_length += b' ' * (HEADER - len(send_length))
                client.send(send_length)
                client.send(message)

                send_list.append(item)

                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    quit()
            

    
def recieve():
    # Client msglist is to be used with GUI
    global client_msglist
    client_msglist = []
    global msg
    while True:
        msg = client.recv(2048).decode(FORMAT)
        if msg:
            client_msglist.append(msg)
            print(msg)

            try:
                globals.gui_incoming.append(msg)
            except:
                print("Error: 'gui_incoming' is not defined by globalsrf")
        if connected == False:
            quit()




# Accidentally had this on a while loop, generating hundreds of threads a second
# Whoopsies! (It's fixed now)
def start():
    globals.init()
    connect()
    thread = threading.Thread(target = send)
    thread2 = threading.Thread(target = recieve)
    thread.start()
    thread2.start()
    clientgui.main_screen()

if __name__ == "__main__":
    global connected
    connected = True
    start()