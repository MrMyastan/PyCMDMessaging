import socket
import threading

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def ConnectionHandler(threadConn, threadAddr):
    username = threadConn.recv(1024)
    connections[threadConn] = username
    threadConn.sendall(b'OK')
    with threadConn:
        while True:
            threadData = threadConn.recv(1024)
            if not threadData:
                connections.remove(threadConn)
                break
            RelayMessage(threadData, username, threadConn)

def RelayMessage(message, displayName, sourceConn):
    finalMessage = displayName + b': ' + message
    for socket in connections:
        if socket != sourceConn:
            socket.sendall(finalMessage)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    connections = {}
    s.bind((HOST, PORT))
    s.listen()
    while True:    
        conn, addr = s.accept()
        threading.Thread(target=ConnectionHandler, args=(conn, addr,)).start()



