from socket import *
import time

def get(fileName: str)-> bytes:
    with open('files/' + fileName, 'rb') as imageFile:
        data = imageFile.read()
    return data

def post(fileName: str, file: bytes) -> None:
    try:
        with open('files/downloaded_' + fileName, 'xb') as localFile:
            localFile.write(file)
    except FileExistsError:
        raise ValueError

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
        content = get(fileName)
        fileSize = str(len(content))
        
        # Sends file to the server
        message = f'{action} {fileName} {fileSize}'
        clientSocket.sendto(message.encode(), serverAddress)
        time.sleep(0.5) # Delay to avoid packet loss
        
        # Envia o arquivo em partes
        for i in range(0, int(fileSize), buffer_size):
            chunk = content[i:i+buffer_size]
            clientSocket.sendto(chunk, serverAddress)
            time.sleep(0.01) # Delay to avoid packet loss

        #response, _ = clientSocket.recvfrom(buffer_size)
        #print(f'Server response: {response.decode()}')

    # Get file from server
    elif action == 'get':
        message = f'{action} {fileName} None'
        clientSocket.sendto(message.encode(), serverAddress)

        message, serverAddress = clientSocket.recvfrom(buffer_size)
        fileSize = int(message.decode()) 
        print(f'File "{fileName}" is {fileSize} bytes.')
        
        # Recebe o arquivo em partes
        received_data = b""
        while len(received_data) < fileSize:
            chunk, _ = clientSocket.recvfrom(buffer_size)
            received_data += chunk
        response = received_data # Removed decode() outside Publisher.py
        
        if response != 'None':
            #content = response.split(" ", 1) Removed, no need to split
            content = response
            # print(f'File "{fileName}" with content: {content}')
            post(fileName, content)
            
            print(f'File "{fileName}" downloaded successfully.')

    else:
        print('Invalid action. Use "get", "post", or "close".')

clientSocket.close()