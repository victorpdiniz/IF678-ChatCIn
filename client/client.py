from socket import *
from utils.FileManager import FileManager

serverPort = 1057
clientPort = 1058
buffer_size = 1024
host = 'localhost'

serverAddress = (host, serverPort)
clientAddress = (host, clientPort)

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(clientAddress)

print('The client is ready.')

while True:
    action = input('Enter action (get/post/close): ').strip().lower()

    if action == 'close':
        clientSocket.sendto('close'.encode(), serverAddress)
        break

    fileName = input('Enter file name (with extension): ').strip()

    # Act depends on the action
    
    # Post file to server
    if action == 'post':
        content = FileManager.actFile(fileName, 'get')

        # Sends file to the server
        message = f'{action} {fileName} {content}'
        clientSocket.sendto(message.encode(), serverAddress)

    # Get file from server
    elif action == 'get':
        message = f'{action} {fileName} None'
        clientSocket.sendto(message.encode(), serverAddress)

        data, serverAddress = clientSocket.recvfrom(buffer_size)
        response = data.decode()

        if response != 'None':
            fileName, content = response.split(" ", 1)
            
            FileManager.actFile(fileName, 'post', content)
            
            print(f'File "{fileName}" downloaded successfully.')

    else:
        print('Invalid action. Use "get", "post", or "close".')

clientSocket.close()