from socket import *

serverPort = 1057
clientPort = 1058
host = 'localhost'
serverAddress = (host, serverPort)
clientAddress = (host, clientPort)

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(clientAddress)
print('The client is ready to send.')

while True:
    message = input('Input lowercase sentence:')
    clientSocket.sendto(message.encode(), serverAddress)
    
    modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
    print(f'Upper sentence received from server {serverAddress}: {modifiedMessage.decode()}.')
    
    if modifiedMessage.decode() == 'QUIT':
        break
    
clientSocket.close()