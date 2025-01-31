from socket import *
from utils.FileManager import FileManager

serverPort = 1057
buffer_size = 1024
host = 'localhost'
serverAddress = (host, serverPort)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)

print('The server is ready.')

while True:
    
    # Receive message and decode
    file, clientAddress = serverSocket.recvfrom(buffer_size)
    action, fileName, content = file.decode().split(" ", 2)
    
    print(f'Command received from client: {action} {fileName}.')
    
    if action == 'close':
        break
    
    # Act on file
    returned = FileManager.actFile(fileName, action, content)
    print(f'Command accomplished, send response to: {clientAddress}.')
    
    # If there is a file to send back
    if returned is not None:
        returned = f'{fileName} {returned}'
        serverSocket.sendto(returned.encode(), clientAddress)
    
    else:
        serverSocket.sendto('None'.encode(), clientAddress)
    
    
serverSocket.close()