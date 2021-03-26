# HANQING GUAN z5213081
# COMP3331 Assignment
# server code
# some code use the server of Multi-threaded Code (Python) in COMP3331 Assignment webpage

from socket import *
from serverHelper import *
import threading
import time
import datetime as dt
import sys
import pickle

# check if the input valid
if len(sys.argv) < 3 or len(sys.argv) > 4:
    print("error input")
    exit(1)

# get the server port and password
serverPort = int (sys.argv[1])
password = sys.argv[2]


t_lock=threading.Condition()

#store clients info in this list
clients=[]
SHUTDOWN = False


def server_run(connectionSocket, clientAddress):
    global t_lock
    global clients
    global SHUTDOWN

    # check if the client first time input
    first = True
    while(SHUTDOWN == False):
        # recieve the message from client
        message = connectionSocket.recv(2048).decode('utf-8')

        # if message is empty, 
        # that means this is send from check socket to check if server is cloesd
        # just close the connect and break
        if (message == ""):
            connectionSocket.close()
            break
        
        # if fist time input, that means useful client connected
        if (first):
            frist = False
            print("Client connected")
        
        # get the username of this client connection
        client_user = get_client_username(clients, clientAddress)
        serverMessage = ""

        with t_lock:
            messages = message.split( )

            # check the command
            if (messages[0] == "LOGIN"):
                # if command = login, run login
                serverMessage = login(messages, serverMessage, clients)
                
                if (serverMessage == "Welcome to the forum"):

                    # if login successfully, add this client and its username, connectSocket to clients list
                    print(messages[1] + " successful login")
                    clients.append({'connectSocket': connectionSocket, 'clientAddress': clientAddress, 'username': messages[1]})

            elif (messages[0] == 'REGISTER'):
                # if command = register, run register
                serverMessage = register(messages)

            elif (messages[0] == "CRT"):
                # if commadn = CRT, run create thread
                print (client_user + " issued CRT command")
                serverMessage = create_thread(messages, client_user)
                
            elif (messages[0] == "MSG"):
                # if commadn = MSG, run post message
                print (client_user + " issued MSG command")
                serverMessage = post_message(messages, client_user)

            
            elif (messages[0] == "DLT"):
                # if commadn = DLT, run delete message
                print (client_user + " issued DLT command")
                serverMessage = delete_message(messages, client_user)
            
            elif (messages[0] == "EDT"):
                # if commadn = EDT, run edit message
                print (client_user + " issued EDT command")
                serverMessage = edit_message(messages, client_user)

            elif (messages[0] == "LST"):
                # if commadn = LST, run list threads
                print (client_user + " issued LST command")
                serverMessage = list_threads(messages)
            
            elif (messages[0] == "RDT"):
                # if commadn = RDT, run read thread
                print (client_user + " issued RDT command")
                serverMessage = read_thread(messages)


            elif (messages[0] == "UPD"):
                # if commadn = UPD, check the upload file condition
                print (client_user + " issued UPD command")
                serverMessage = check_upload_file(messages) + "\n"

                if (serverMessage == "You can upload file\n"):
                    # if pass the check, send message to client
                    connectionSocket.send(serverMessage.encode('utf-8'))
                    
                    # get the upload file name
                    thread_name = messages[1]
                    filename = thread_name + "-" + messages[2]
                    
                    # receive the file data from client and upload it
                    data = pickle.loads(connectionSocket.recv(8192))["file"]
                    upload_file(filename, data)
                    print("file uploading.....")

                    serverMessage = upload_file_message(thread_name, client_user, messages[2])

            elif (messages[0] == "DWN"):
                # if commadn = DWN, check the download file condition
                print (client_user + " issued DWN command")
                serverMessage = check_download_file(messages) + "\n"

                if (serverMessage == "You can download file\n"):
                    # if pass the check, send message to client
                    connectionSocket.send(serverMessage.encode('utf-8'))
                    
                    # get data of download file and send it to client
                    time.sleep(0.1)
                    data = get_download_data(messages)
                    connectionSocket.sendall(pickle.dumps({"file": data}))
                    print("file downloading.....")

                    serverMessage = messages[2] + " downloaded from Thread " + messages[1]

            elif (messages[0] == "RMV"):
                # if commadn = DWN, run remove thread
                print (client_user + " issued RMV command")
                serverMessage = remove_thread(messages, client_user)
                
            elif (messages[0] == "XIT"):
                # if commadn = XIT, serverMessage = goodbye
                print (client_user + " issued XIT command")
                serverMessage = "Goodbye"

                # find this client from list clients
                # remove this client from list
                for client in clients:
                    if (client['clientAddress'] == clientAddress):
                        clients.remove(client)
                        break;
                        
                # send the server message to client, close the connection, break
                serverMessage = serverMessage + "\n"
                connectionSocket.send(serverMessage.encode('utf-8'))
                connectionSocket.close()
                break;

            elif (messages[0] == "SHT"):
                # if commadn = SHT
                print (client_user + " issued SHT command")

                # check if the input valid
                if (len(messages) != 2):
                    serverMessage = "Incorrect syntax for SHT"
                    
                if (password != messages[1]):
                    # check if the password is correct
                    serverMessage = "Incorrect password"

                else:
                    # if password correct, send message to shut down server, run shut down
                    serverMessage = "Goodbye. Server shutting down\n"
                    print("Server shutting down\n")
                    shut_down()

                    # close every client in clients
                    for client in clients:
                        client['connectSocket'].send(serverMessage.encode('utf-8'))
                        client['connectSocket'].close()
                        time.sleep(0.1)
                    
                    time.sleep(1)
                    print("Server closed.\n")
                    
                    # declare empty client, exit
                    clients = []
                    os._exit(1)
            else:
                # if not valid command
                serverMessage = "Invalid command"
            
            # output serverMessage
            print(serverMessage + "\n")

            # send message to client
            serverMessage = serverMessage + "\n"
            connectionSocket.send(serverMessage.encode('utf-8'))

            #notify the thread waiting
            t_lock.notify()

    

# get and set the server Socket
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('localhost', serverPort))
serverSocket.listen(2)


print('Server is ready for service')
print("Waiting for clients")

# if the shutdown is false, run threads
while SHUTDOWN == False:
    connectionSocket, address = serverSocket.accept()
    recv_thread=threading.Thread(target=server_run, args=[connectionSocket, address])
    recv_thread.daemon=True
    recv_thread.start()
    


# Close the server
serverSocket.close()