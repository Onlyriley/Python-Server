from contextlib import redirect_stdout
import PySimpleGUI as sg
import client
import globals
import threading
import time
def gui_login():
    global username
    sg.change_look_and_feel('Dark Blue 3')



    layout = [  [sg.Text('Please enter your username')],
                [sg.Input(key='USRNAME'), sg.Text(size=(12,1), key='-OUT-')],
                [sg.Button('Go', bind_return_key=True), sg.Button('Exit'), sg.Debug()]  ]
    window = sg.Window('PyChat Login', layout)
    while True:
        event, values = window.read()
        if event in (None, 'Exit'):
            break
        if event == 'Go':
            username = values['USRNAME']
            print(username)
            window['-OUT-'].Update(values['USRNAME'])
            window.close()
            return username
    window.close()

def chat():
    global guimsglist
    global main_window
    while True:    
        try:
            for msg in globals.gui_incoming:
                if msg not in guimsglist:
                    main_window['MessageBox'].Update(main_window['MessageBox'].get() + '\n' + msg)
                    guimsglist.append(msg)
        except:
            print("error")



def main_screen():
    chat_thread = threading.Thread(target=chat)
    chat_thread.start()

    globals.gui_init()
    global guimsglist
    global main_window
    guimsglist = []
    global usr_message
    sg.change_look_and_feel('Dark Blue 3')
    layout = [  [sg.Text('Chat')],

    # I don't think multiline is going to work here
                [sg.Multiline(default_text = "Welcome to PyChat, incoming message will be displayed here", auto_refresh = True, key = 'MessageBox', autoscroll = True, size = (64, 24))],
                [sg.Input(key='USRINPUT')],
                [sg.Button('Send', bind_return_key = True), sg.Button('Exit')]  ]
    main_window = sg.Window('PyChat', layout)
    while True:

        event, values = main_window.read()

        if event in (None, 'Exit'):
            main_window.close()
            quit()
        if event == 'Send':
            usr_message = values['USRINPUT']
            # print(usr_message)
            globals.recieve_list.append(usr_message)
            main_window['USRINPUT'].Update('')





if __name__ == "__main__":
    #gui_login()
    #main_screen()
    chat_thread = threading.Thread(target=chat)