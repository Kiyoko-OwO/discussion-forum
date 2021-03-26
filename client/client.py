# HANQING GUAN z5213081
# COMP3331 Assignment
# client code

import time
import threading
from socket import *
import sys
import os
import pickle


# check if the input valid
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("error input")
    exit(1)

# helper function to download the data to file
def download(messages, data):
    file = open(message.split(" ")[2], 'wb')
    file.write(data)
    file.close

# auto refresh thread to check if the server closed
def check_alive(serverName, serverPort):

    while 1:
        time.sleep(0.1)
        s = socket(AF_INET, SOCK_STREAM)
        s.settimeout(3)
        result = s.connect_ex((serverName, serverPort))
        
        if result != 0:
            print ("Goodbye. Server shutting down\n")
            clientSocket.close()
            os._exit(1)
        else:
            s.send("".encode('utf-8'))
            s.close()



        

# get the servername and server port
serverName = sys.argv[1]
serverPort = int (sys.argv[2])

# create clientSocket and connet it to server
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

# start to run the thread
check = threading.Thread(target=check_alive, args=[serverName, serverPort])
check.daemon=True
check.start()

# login part
while 1:
    username = input('Enter username: ')
    password = input('Enter password: ')

    # create the login message send to server
    info_login = 'LOGIN' + ' ' + username + ' ' + password;
    clientSocket.send(info_login.encode('utf-8'))

    # get the message from server and output it
    feedback = clientSocket.recv(2048).decode('utf-8')
    print(feedback);

    # if the login successful, go to next part
    if (feedback == "Welcome to the forum\n"):
        break;
    elif (feedback == "Invalid Username\n"):
        # if the username does not exists, ask if client want to register
        print ("Register a new user. \n If you do not want to register, just put username and password empty.")
        username = input('Enter username: ')
        password = input('Enter password: ')
        
        info_register = 'REGISTER ' + username + ' ' + password
        clientSocket.send(info_register.encode('utf-8'))

        feedback = clientSocket.recv(2048).decode('utf-8')
        print(feedback);

# order part
while 1:
    # shows the prompt and information
    print ("information of commands:")
    print ("CRT: Create Thread")
    print ("MSG: Post Message")
    print ("DLT: Delete Message")
    print ("EDT: Edit Message")
    print ("LST: List Threads")
    print ("RDT: Read Thread")
    print ("UPD: Upload File")
    print ("DWN: Download File")
    print ("RMV: Remove Thread")
    print ("XIT: Exit")
    print ("SHT: Shutdown Server")
    print ("Enter one of the following commands: CRT, MSG, DLT, EDT, LST, RDT, UPD, DWN, RMV, XIT, SHT: \n")

    # get the input message
    message = input()
    print(" ")
    feedback = ""

    # if message is not useful, continue
    if (message == "" or message == "\n"):
        continue
    
    # split the message
    messages = message.split(" ")

    if (messages[0] == "UPD"):
        
        # if command = UPD, check if input valid
        if (len(messages) != 3):
            feedback = "Incorrect syntax for UPD"
            print(feedback+"\n")
            continue
        
        # check if this file exists
        filename = messages[2]
        if os.path.exists(filename) and os.path.isfile(filename):
            
            # if exists, send request to server
            clientSocket.send(message.encode('utf-8'))

            feedback = clientSocket.recv(2048).decode('utf-8')

            # if server check and agree the request, upload file, send to server
            if (feedback == "You can upload file\n"):
                print(feedback);

                file = open(filename, "rb")
                data = file.read()
                file.close

                clientSocket.sendall(pickle.dumps({"file": data}))
                print ("uploading....\n")
                    
                feedback = clientSocket.recv(2048).decode('utf-8')
            
        else:
            # if file does not exist, continue to next loop
            print("This file " + filename +" does not exist\n")
            continue

    elif (message.split(" ")[0] == "DWN"):

        # if command = DWN, send the request to server
        clientSocket.send(message.encode('utf-8'))
        feedback = clientSocket.recv(2048).decode('utf-8')

        # if server check and agree the request, download file from server
        if (feedback == "You can download file\n"):
            print(feedback);

            data = pickle.loads(clientSocket.recv(8192))["file"]
            print ("downloading....\n")
            download(message, data)

            feedback = clientSocket.recv(2048).decode('utf-8')

    else:
        # send request to server and get feedback
        clientSocket.send(message.encode('utf-8'))

        feedback = clientSocket.recv(2048).decode('utf-8')

    print(feedback);

    # if feedback means end the process, just break and finish 
    if (feedback == "Goodbye\n" or feedback == "Goodbye. Server shutting down\n"):
        break;

# Close the socket
clientSocket.close()
