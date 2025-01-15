from socket import *

serverPort = 1057
host = 'localhost'
serverAddress = (host, serverPort)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)

print('The server is ready to receive.')

while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    print(f'Message received from client {clientAddress}: {message.decode()}.')
    
    modifiedMessage = message.decode().upper()
    print(f'Message sended: {modifiedMessage}.')
    
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)
    
    if modifiedMessage == 'QUIT':
        break

serverSocket.close()