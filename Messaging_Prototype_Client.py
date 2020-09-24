import socket
import threading
import time
import argon2

# place to connect to
HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

# grab the argon2 passowrd hasher
PH = argon2.PasswordHasher()

# message receiver/printer
def inc_msg_handler(socket):
    # set up context manager
    with socket: 
        # loop to make sure its always waiting for and printing messages
        while True:  
            # receive and if theres no data (which should only happen if the connection closes because its blocking), quit
            data = socket.recv(1024)
            if not data:
                break
            # get string representation of the returned bytes and then print everything except the b'  ', calling str() is probably unnecessary because i think print calls it anyway (or maybe repr()?) and i think encode will get rid of the b' '
            print(str(data)[2:-1])

# prompt user if they want to create or login, only in its own method to make recursion after an invalid input easier
def create_or_login(socket):
    # prompt user and ask what they want to do
    createAccount = input("press 0 to login and 1 to create an account: ")
    # if they want to create account or login call that method and pass in the socket being used for communicating with the message server (that was passed to this method), honestly not sure why im passing in the socket but just using the var holding the password hasher wihtout passing it in to those methods but I'm rambling now
    if createAccount == "0":
        login(socket)
    if createAccount == "1":
        create_account(socket)
    # if the input was invalid, try again
    else:
        create_or_login()
        
# function for logging in
def login(socket):
    # set up context manager for the socket
    with socket:
        # tell the server we are about to try to login and wait for a response before continuing, only response should be OK so I'm not checking it yet
        socket.sendall(b'LI')
        socket.recv(8)
        # grab the username for the account the user wants to log in to
        loginUsername = input("Username: ")
        # encode and send the username to the server
        socket.sendall(bytes(loginUsername, 'utf-8'))
        # wait for the password hash for the account
        accountPass = socket.recv(1024)
        # wrap verify in try block to catch the exception thrown if they don't match
        try:
            # ask user for password and check it against the hash, and signal the server if login was successful, and wait for response, again the only response should be OK so I wont be checking
            PH.verify(accountPass, input("Password: "))
            socket.sendall(b'SL')
            socket.recv(8)
        except VerifyMismatchError:
            # if the login was unsuccessful the exception should be thrown, this block should be entered, it shouldnt have send the successful login signal and instead will tell the user the password was incorrect, send the failed login signal, and exit
            print("Incorrect Password")
            socket.sendall("FL")
            # add time wait?
            sys.exit("Incorrect Password")
        # if all goes well, print
        print("Login successful")


def create_account(socket):
    # set up context manager
    with socket:
        # get username to create account with
        newUsername = input("Please enter a username: ")
        # hehe
        if newUsername == "a username":
                print("haha very funny but thats your username now")
        else:
            print("Good choice, good choice")
        # get and hash the password
        newPassHash = PH.hash(input("Now choose a password: "))
        # let the server know we want to create an account and wait for a response before continuing, only response should be OK so I'm not checking it yet
        socket.sendall(b'CA')
        socket.recv(8)
        # tell the server the name for the new account, and wait for a response
        socket.sendall(bytes(newUsername, 'utf-8'))
        response = socket.recv(8)
        # if the server responds that the name is taken then let the user know they are unoriginal and quit, still need to figure out a way to have it try again
        if response == b'TAKEN':
            print("Sorry, you are unoriginal and your username is already in use")
            sys.exit("Attempted to create an account with in use name")
        # only other response should be OK so im not gonna check for that and then i encode and send the password hash off to the sever, only response should be OK so again im not checking for it
        socket.sendall(bytes(newPassHash, 'utf-8'))
        socket.recv(8)
        # let the user know they are good to go
        print("Success! You are now " + newUsername + " on the PyCmdLineMessenger and good to go!")

# create socket and use with context manager
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    # connect to server
    s.connect((HOST, PORT))
    print("You are connected!, starting thread")
    
    # call the function to create an account or login
    create_or_login(s)
    
    # spawn incoming message handler thread
    threading.Thread(target=IncMsgHandler, args=(s,)).start()
    
    # start loop to make sure its always waiting or sending
    while True:
        # wait for/get input
        message = input()
        # if its quit, break the loop and then the program should finish, still need to figure out how to gracefully close the other threads, if i dont everything kinda crashes cuz its listening on the socket and then it gets forcibly closed but i thought the context manager was supposed to handle that, anywayyyyy
        if message == "quit":
            break
        # if theres a message that isn't quit send it off to the server where the receiver thread for this client should catch it and relay it to the other clients
        s.sendall(bytes(message, 'utf-8'))
