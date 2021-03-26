# HANQING GUAN z5213081
# COMP3331 Assignment
# server helper functions


import os
import re

# save thr threads
threads = []

# get the client's username from clients list
def get_client_username(clients, client_addr):
    for client in clients:
        if (client['clientAddress'] == client_addr):
            return client['username']
    
    return '';

# make the messages list to messages string
def getmessage(messages):
    message = ""
    for m in messages:
        message += m + " "
    
    return message

# check if the username in message exist in credentials.txt
def check_name_exist(username):
    file = open("./credentials.txt", "r")
    credentials = file.readlines()
    file.close()

    for line in credentials:
        line = line.split( )
        if (line[0]+":" == username):
            return True
    
    return False

# check if the line is a message
def check_message(line):
    words = line.split( )
    if (words[0].isdigit() and check_name_exist(words[1])):
        return True
    else:
        return False

# get new message number
def get_m_number(contents):
    # use counter to count the message number
    counter = 1

    for line in contents:
        if (check_message(line)):
            counter+=1

    return counter

# login helper function
def login(messages, serverMessage, clients):
    # check if the input valid
    if (len(messages) != 3):
        serverMessage = "invalid input"
        return serverMessage

    username = messages[1]
    password = messages[2]

    # check if there is other client login this username
    for client in clients:
        if client['username'] == username:
            serverMessage = "this username already logged in by other client"
            return serverMessage

    # open the file 
    file = open("credentials.txt", "r")
    credentials = file.readlines()
    file.close()
                
    

    for line in credentials:
        line = line.split( )
        
        if (line[0] == username):
            if (line[1] == password):
                # if the username and password correct
                serverMessage = "Welcome to the forum"
            else:
                # if the password is not correct
                serverMessage = "Invalid password"
                        
            break;
                
    if (serverMessage == ""):
        # if there is no this username
        serverMessage = "Invalid Username"

    return serverMessage;

def register(messages):
    # check if the input valid
    if (len(messages) != 3):
        serverMessage = "invalid input"
        return serverMessage

    username = messages[1]
    password = messages[2]

    # check if the username and password valid, comment because do not need to test
    # except space, alomost all of the character is valid
    # re_exp = '[A-Za-z0-9~!@#\$%\^&\*_-\+=`\|\\\(\)\{\}\[\]:;\"\'<>,\.\?/]+'
    # if re.search(re_exp, username) and re.search(re_exp, password):
    #     serverMessage = "invalid username or password"
    #     return serverMessage
    
    # if valid, add new username and password to credentials.txt
    newline = username + ' ' + password + "\n"
    file = open("credentials.txt", "a")
    file.write(newline)
    file.close()

    serverMessage = "Successful Register. Please log in."

    return serverMessage

# CRT create thread helper function
def create_thread(messages, username):
    # check if the input is valid
    if (len(messages) != 2):
        serverMessage = "invalid input"
        return serverMessage

    # get the thread name and check if this thread exists
    thread_name = messages[1]
    if (os.path.exists(thread_name) and thread_name in threads):
        # if this thread exists
        serverMessage = "Thread " + thread_name + " exists"

    else:
        # if this thread does not exists, create a new file for new thread
        # put the creator username in first line
        file = open(thread_name, "w")
        file.write(username + "\n")
        file.close

        # add the thread in list
        threads.append(thread_name)
        serverMessage = "Thread " + thread_name + " created"
    
    return serverMessage

# MSG post message helper
def post_message(messages, username):
    # check if the input is valid
    if (len(messages) < 3):
        serverMessage = "invalid input"
        return serverMessage
    
    thread_name = messages[1]
    message = getmessage(messages[2:])
    
    # check if the thread exists
    if (os.path.exists(thread_name) and thread_name in threads):
        # if thread exists, open thread and get the m_number for new message
        file = open(thread_name, "r")
        m_number = get_m_number(file.readlines())
        file.close

        # add new message to the end of the thread file
        file = open(thread_name, "a")
        file.write(str(m_number) + " " + str(username) + ": " + message + "\n")
        file.close
        serverMessage = "Message posted to " + thread_name + " thread"

    else:
        # if the thread name does not exist
        serverMessage = "Thread " + thread_name + " does not exist"
    
    
    return serverMessage

# DLT delete message helper function
def delete_message(messages, username):
    # check if the input valid
    if (len(messages) != 3):
        serverMessage = "invalid input"
        return serverMessage

    thread_name = messages[1]
    m_number = messages[2]
    serverMessage = ""

    if (os.path.exists(thread_name) and thread_name in threads):
        # if the thread exists, read thread file
        file = open(thread_name, "r")
        contents = file.readlines()
        file.close

        # find the message
        for line in contents:
            words = line.split( )
            if (words[0] == str(m_number) and check_message(line)):
                # if find the message, check if username is this username
                if (words[1] == username+":"):
                    # if username is same, delete the message
                    # get new content of file and write in file

                    # store old content
                    temp_content = contents
                    # store new content
                    new_content = ""
                    # count the message number
                    counter = 1

                    for temp_line in temp_content:
                        if (temp_line == line):
                            # ignore the line we want to delete
                            continue
                        if (counter == 0 or check_message(temp_line) == False):
                            # if not message line, just add to new_content
                            new_content += temp_line
                        else:
                            # if is message line, put new message number wit the messgae in new_content
                            temps = temp_line.split( )
                            line_message = str(counter) + " " + ''.join(temps[1]) + " " + ''.join(temps[2:]) + "\n"
                            new_content += line_message
                            counter+=1

                    # write new_content to thread file, DLT successful
                    file = open(thread_name, "w")
                    file.write(new_content)
                    file.close

                    serverMessage = "Message " + m_number + " in " + thread_name + " thread has been deleted"
                else:
                    # if username is incorrect, cannot delete the message
                    serverMessage = "Message " + m_number + " in " + thread_name + " thread was create by another user and cannot be deleted"
                
                break;
        
        if (serverMessage == ""):
            # if message does not exits
            serverMessage = "Message " + m_number + " in " + thread_name + " thread does not exist"

    else:
        # if the thread name does not exist
        serverMessage = "Thread " + thread_name + " does not exist"
    
    return serverMessage

# EDT edit message helper function
def edit_message(messages, username):
    # check if input valid
    if (len(messages) < 4):
        serverMessage = "invalid input"
        return serverMessage

    thread_name = messages[1]
    m_number = messages[2]
    new_message = getmessage(messages[3:])
    serverMessage = ""

    if (os.path.exists(thread_name) and thread_name in threads):
        # if the thread exists, get content of thread file
        file = open(thread_name, "r")
        contents = file.readlines()
        file.close

        
        for line in contents:
            words = line.split( )
            if (words[0] == str(m_number) and check_message(line)):
                # get the message
                if (words[1] == username+":"):
                    # if username is correct, change the old message to new message
                    old_message = ' '.join(words[2:])
                    new_line = line.replace(old_message, new_message)

                    # replace the messageline, and write new line with the other contents to thread file
                    file = open(thread_name, "w")
                    file.write(''.join(contents).replace(line, new_line))
                    file.close

                    serverMessage = "Message " + m_number + " in " + thread_name + " thread has been edited"
                else:
                    # if username is incorrect
                    serverMessage = "Message " + m_number + " in " + thread_name + " thread belongs to another user and cannot be edited"
                
                break;
        
        if (serverMessage == ""):
            # if the message number does not exist
            serverMessage = "Message " + m_number + " in " + thread_name + " thread does not exist"

    else:
        # if the thread does not exist
        serverMessage = "Thread " + thread_name + " does not exist"
    
    return serverMessage

# LST list threads helper function
def list_threads(messages):
    # check if the input valid
    if (len(messages) != 1):
        serverMessage = "Incorrect syntax for LST"
        return serverMessage

    serverMessage = ""

    # get all threads
    for name in threads:
        if (os.path.exists(name)):
            serverMessage += name + "\n"
    
    if (serverMessage == ""):
        # if there is no threads
        serverMessage = "No threads to list"
    else:
        serverMessage = "The list of active threads:\n" + serverMessage

    return serverMessage

# RDT read thread helper function
def read_thread(messages):
    # check if the input valid
    if (len(messages) != 2):
        serverMessage = "Incorrect syntax for RDT"
        return serverMessage
    
    thread_name = messages[1]
    serverMessage = ""

    # check if thread exists
    if (os.path.exists(thread_name) and thread_name in threads):
        # get the contents of the thread
        file = open(thread_name, "r")
        contents = file.readlines()
        if (len(contents) == 1):
            # if there is no contents
            serverMessage = "Thread " + thread_name + " is empty"
        else:
            # get all contents except the first line
            first = True
            for line in contents:
                if first == True:
                    first = False
                    continue
                else:
                    serverMessage += line

        file.close

    else:
        # if thread does not exist
        serverMessage = "Thread " + thread_name + " does not exist"
    
    return serverMessage

# RMV remove thread helper function
def remove_thread(messages, username):
    # check if the input invalid
    if (len(messages) != 2):
        serverMessage = "Incorrect syntax for RMV"
        return serverMessage

    thread_name = messages[1]
    serverMessage = ""

    # check if the thread exists
    if (os.path.exists(thread_name) and thread_name in threads):
        # get the username
        file = open(thread_name, "r")
        contents = file.readlines()
        file.close

        # check if the username is this username
        if (contents[0] == username+"\n"):
            # if the username correct, remove the thread
            serverMessage = "The thread " + thread_name + " has been removed"

            # remove files related to this thread
            os.remove(thread_name)
            threads.remove(thread_name)
            for file in os.listdir(os.getcwd()):
                if ("-" in file):
                    file_thread = file.split("-")
                    if (file_thread[0] == thread_name and os.path.isfile(file)):
                        os.remove(file)

        else:
            # if username is incorrect
            serverMessage = "The thread " + thread_name + " was created by another user and cannot be removed"

    else:
        # if thread does not exists
        serverMessage = "Thread " + thread_name + " does not exist"
    
    return serverMessage

# UPD helper function check if can upload file
def check_upload_file(messages):
    # check if input is valid
    if (len(messages) != 3):
        serverMessage = "Incorrect syntax for UPD"
        return serverMessage

    thread_name = messages[1]
    filename = messages[2]

    # check if the thread exists
    if (os.path.exists(thread_name) and thread_name in threads):
        newname = thread_name + "-" + filename

        # check if the file exists in thread
        if (os.path.exists(newname)):
            serverMessage = newname + " exists"
        else:
            # if does not exist, client can upload file
            serverMessage = "You can upload file"
            
    else:
        serverMessage = "Thread " + thread_name + " does not exist"
    
    return serverMessage

# UPD helper function to add upload message to thread
def upload_file_message(thread_name, username, filename):
    file = open(thread_name, "a")
    file.write(username + " uploaded " + filename + "\n")
    file.close
    serverMessage = username + " uploaded file " + filename + " to " + thread_name + " thread"
    return serverMessage

# UPD helper function to get the upload file to server directory
def upload_file(filename, data):
    file = open(filename, 'wb')
    file.write(data)
    file.close

# DWN helper function to check if can download file
def check_download_file(messages):
    # check if the input valid
    if (len(messages) != 3):
        serverMessage = "Incorrect syntax for DWN"
        return serverMessage

    thread_name = messages[1]
    filename = messages[2]
    file = thread_name + "-" + filename
    
    # check the file exists
    if (os.path.exists(thread_name) and thread_name in threads):
        if (os.path.exists(file)):
            # if exists, client can download
            serverMessage = "You can download file"
        else:
            serverMessage = "file " + filename + " does not exist in thread " + thread_name
            
    else:
        serverMessage = "Thread " + thread_name + " does not exist"
    
    return serverMessage

# DWN helper function to get the data of the file
def get_download_data(messages):
    thread_name = messages[1]
    filename = messages[2]
    file = thread_name + "-" + filename
    file = open(file, "rb")
    data = file.read()
    file.close

    return data

# SHT helper function to delete all files expect the program file in directory
def shut_down():
    for file in os.listdir(os.getcwd()):
        if (file == "server.py" or file == "serverHelper.py"  or os.path.isdir(file)):
            continue
        else:
            os.remove(file)