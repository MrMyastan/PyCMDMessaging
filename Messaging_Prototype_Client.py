import socket
import threading
import time
import argon2

# place to connect to
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

PH = argon2.PasswordHasher()

# async message receiver/printer
def IncMsgHandler(socket):
    with socket:    
        while True:  
            data = socket.recv(1024)
            if not data:
                break
            print(str(data)[2:-1])

def CreateOrLogin(socket):
    createAccount = input("press 0 to login and 1 to create an account: ")
    if createAccount == "0":
        Login(socket)
    if createAccount == "1":
        CreateAccount(socket)
    else:
        CreateOrLogin()

def Login(socket):
    socket.sendall(b'LI')
    socket.recv(8)
    loginUsername = input("Username: ")
    socket.sendall(bytes(loginUsername, 'utf-8'))
    accountPass = socket.recv(1024)
    PH.verify(accountPass, input("Password: "))

def CreateAccount(socket):
    with socket:
        newUsername = input("Please enter a username: ")
        if newUsername == "a username":
                print("haha very funny but thats your username now")
        else:
            print("Good choice, good choice")
        newPassHash = PH.hash(input("Now choose a password: "))
        socket.sendall(b'CA')
        response = socket.recv(8)
        socket.sendall(bytes(newUsername, 'utf-8'))
        response = socket.recv(8)
        if response == b'TAKEN':
            print("Sorry, you are unoriginal and your username is already in use")
            CreateAccount
            return
        socket.sendall(bytes(newPassHash, 'utf-8'))
        response = socket.recv(8)
        print("Success! You are now " + newUsername + " on the PyCmdLineMessenger and good to go!")

# create socket and use with context manager
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    # connect to server
    s.connect((HOST, PORT))
    print("You are connected!, starting thread")
    
    CreateOrLogin(s)

    # picks a diplay name and waits for confirmation (actually there isn't any error checking or whatever so basically it just blocks if the server crashes
    # s.sendall(bytes(input("Pick a display name: "), 'utf-8'))
    # s.recv(8)
    
    # spawn incoming message handler thread
    threading.Thread(target=IncMsgHandler, args=(s,)).start()
    
    # input and sending messages
    while True:
        message = input()
        if message == "quit":
            break
        s.sendall(bytes(message, 'utf-8'))
   
       
    #mode = input()
    #if mode == "1":
    #print("mode 1") 
        
    #        data = s.recv(1024)
    #        print(str(data))
    #if mode == "0":
    #    print("mode 0")
    #    while True:
    #        data = s.recv(1024)
    #        print(str(data))

    #createAccount = input("press 0 to login and 1 to create an account: ")
    #if createAccount != "1" or "0":
    #    createAccount = input("press 0 to login and 1 to create an account: ")
