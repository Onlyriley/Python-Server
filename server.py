import socket
import threading
import time
from os.path import exists
import os
import hashlib

HEADER = 64
PORT = 5050
# This doesn't always behave correctly depending on the network type
# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = "45.79.202.153"

ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '/disconnect'
MAX_LOGFILES = 100
LOGFILE_PATH = "logs/"


# I'm storing the password in plain text
# I no one heard that
ADMIN_PASS = "BlueLot33"


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Stores usernames + IPs for reference :)
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
    connected = True
    while connected:
        handle_loop = False
        if msg_update == True:
            try:
                conn.send(f"{msglist[msgcount]}".encode(FORMAT))
            except:
                connected = False
            feedback.append(True)
        while handle_loop == False:
            if feedback.__len__() == 0: handle_loop = True

def msg_recieve(conn):
    try:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        return msg_length
    except:
        # Console already outputs disconnect message, no need to throw error
        # print("[ERROR 10054] Connection no longer available")
        return DISCONNECT_MESSAGE


# Don't use this for user messages!
# Things here are not recorded on the msglist
# (For user commands and interaction)
def msg_send(msg, conn):
    try:
        conn.send(f"{msg}".encode(FORMAT))
    except:
        pass


def user_command(command, conn, addr):

    # This is to recieve from the client in the context of user commands
    # Holy shit, this is getting kinda complicated now
    def CCR(conn):
        msg_length = msg_recieve(conn)
        if msg_length:
            msg_length = int(msg_length)
            msg = msg_recieve(conn)
            return msg

    def auth_list(status, conn, addr):
        global user_groups
        # --- Status definitions ---
        # 0 / unassigned = Normal user
        # 1 = Custom group (future)
        # 2 = Admin
        # 3 = Failed admin login
        if status == 2:
            user_groups[addr] = 2
        if status == 3:
            user_groups[addr] = 3

    # This prompts user for password
    # User gets 3 attempts
    if command == "/admin":
        msg_send("Please enter the admin password:", conn)
        usrpass = CCR(conn)
        if usrpass == ADMIN_PASS: 
            auth_list(2, conn, addr)
            msg_send(f"{userkeys[addr]} has been granted administrator privilages", conn)
            print(f"{userkeys[addr]} has been granted administrator privilages")
        else:
            msg_send("Incorrect Password", conn)

    if command == "/who":
        try:
            if user_groups[addr] == 2:
                msg_send(userkeys, conn)
        except:
            msg_send("Insufficient Permissions", conn)







def handle_client(conn, addr):
    print(f"{addr} CONNECTED")
    connected = True
    global connections
    global validate_users
    connections =+ 1
    connection_auth = False



    # Before moving to normal chat we recieve the client's username
    while connection_auth == False:
        msg_length = msg_recieve(conn)
        if msg_length:
            msg_length = int(msg_length)
            msg = msg_recieve(conn)
            userkeys[addr] = msg
            print(f"{addr} has connected as {userkeys[addr]}")
            msglist.append(f"{userkeys[addr]} has connected")
            connection_auth = True


    while connected:
        msg_length = msg_recieve(conn)
        if msg_length == DISCONNECT_MESSAGE:
            connected = False
            break
        if msg_length:
            msg_length = int(msg_length)
            msg = msg_recieve(conn)
            if msg == DISCONNECT_MESSAGE:
                connected = False
            elif msg[0] == '/':
                user_command(msg, conn, addr)
            else:
                msglist.append(f"{userkeys[addr]}: {msg}")
                print(f"{userkeys[addr]}: {msg}")
        
            

# Checks to make sure user is not banned / kicked
        try:
            if validate_users[userkeys[addr]] == 1:
                print(f"User {userkeys[addr]} was kicked")
                msglist.append(f"User {userkeys[addr]} was kicked")
                del validate_users
                connected = False
        except:
            pass


    conn.close()
    print(f"CONNECTION CLOSED @ {addr}")
    # Deletes IP and username info once a user disconnects so they can reconnect under the same username
    del userkeys[addr]
    try:
        del user_groups[addr]
    except:
        pass
    connections =- 1

# Handles the name of the log file
# (It's lame but I don't know any other good solutions)
def filename():
    for footer in range(MAX_LOGFILES):
        name_of_file = "log" + str(footer) + ".dat"
        file_exist = exists(name_of_file)
        if file_exist == False:
            return str(name_of_file)


def console():
    global msglist
    global msgcount
    global commands
    commands = ['/dump', '/who', '/kick']
    while True:
        statement = input("")

# This outputs the msglist to a logfile
        if statement[0:5] == "/dump":
            file_name = filename()
            dump_statement = statement.split(" ")
            if dump_statement[1] == "help":
                print("USAGE: /dump")
                print("Creates a log file containing messages from clients")
            else:
                try:
                    with open(f"{LOGFILE_PATH}{file_name}", "a") as file:
                        for item in msglist:
                            file.write(f"{item}\n")
                    print(f"Log '{file_name}' created")
                except:
                    print(f"'{LOGFILE_PATH}' does not exist... creating directory")
                    os.mkdir(LOGFILE_PATH)
                    print("Please run command again to save file")

# This will give information of currently connected users
# Specific username can be entered to find IP
        if statement[0:4] == "/who":
            who_statement = statement.split(" ")
            if who_statement.__len__() == 1:
                print(userkeys)
            elif who_statement.__len__() == 2:
                if who_statement[1] == "help":
                    print("USAGE: /who (username)")
                    print("Type /who to view all users")
                elif who_statement[1] in userkeys.values():
                    for address, user in userkeys.items():
                        if user == who_statement[1]:
                            print(f"User '{user}' @ {address}")
                else:
                    print(f"User {who_statement[1]} does not exist")


# This works in junction with handle_client to kick the user through the validate_users variable
        if statement[0:5] == "/kick":
            kick_statement = statement.split(" ")
            if kick_statement.__len__() > 1:
                if kick_statement[1] == "help":
                    print("USAGE: /kick (username)")
                    print("Kicks the specified user")
                elif kick_statement[1] in userkeys.values():
                    for address, user in userkeys.items():
                        if user == kick_statement[1]:
                            global validate_users
                            validate_users[user] = 1


        if statement == "/help":
            for item in commands:
                print(item)
            print("Type command then help to recieve details")


        





def start():
    server.listen()
    print("({}) LISTENING ON PORT {}".format(socket.gethostbyname(socket.gethostname()), PORT))
    global connections
    global validate_users
    global user_groups
    validate_users = {}
    connections = 0
    user_groups = {}

    # Starts the chat thread
    chat_thread_thread = threading.Thread(target=chat_thread)
    chat_thread_thread.start()

    # Starts the username thread
    # This is very lightweight, does not loop
    username_thread = threading.Thread(target=username_config)
    username_thread.start()

    # Starts the console thread
    # This is for running commands from the server side
    # (This will be more useful in development)
    console_thread = threading.Thread(target=console)
    console_thread.start()

    # Starts the main loop
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread2 = threading.Thread(target=handle_inbound, args=(conn,addr))
        thread.start()
        thread2.start()
        time.sleep(.2)
        print(f"{connections} ACTIVE CONNECTIONS")



print("STARTING SERVER...")
if __name__ == "__main__":
    start()