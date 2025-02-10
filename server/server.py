from socket import *
import time

def get(fileName: str)-> bytes:
    with open('files/' + fileName, 'rb') as imageFile:
        data = imageFile.read()
    return data

def post(fileName: str, file: bytes) -> None:
    try:
        with open('files/archived_' + fileName, 'xb') as localFile:
            localFile.write(file)
    except FileExistsError:
        raise ValueError

serverPort = 1057
buffer_size = 1024
host = 'localhost'
serverAddress = (host, serverPort)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)

print('The server is ready.')

while True:
    
    # Receive message and decode
    header, clientAddress = serverSocket.recvfrom(buffer_size) 
    header = header.decode()

    action, fileName, fileSize = header.split(" ", 2)
    if fileSize != 'None':
        fileSize = int(fileSize) # Converte o tamanho do arquivo para inteiro
    returned={}
    print(f'Command received from client: {action} {fileName}({fileSize} bytes).')
    
    if action == 'close':
        break
    elif action == 'post':
    # Recebe o arquivo em partes
        received_data = b""
        while len(received_data) < fileSize:
            chunk, _ = serverSocket.recvfrom(buffer_size)
            received_data += chunk
        returned = post(fileName, received_data)
        
    elif action =='get':
        content = get(fileName)
        fileSize = str(len(content))

        message = f'{fileSize}'
        serverSocket.sendto(message.encode(), clientAddress)
        time.sleep(0.5) # Delay to avoid packet loss
        
        # Envia o arquivo em partes
        for i in range(0, int(fileSize), buffer_size):
            chunk = content[i:i+buffer_size]
            serverSocket.sendto(chunk, clientAddress)
            time.sleep(0.01) # Delay to avoid packet loss (TEMPORARY)

    print(f'Command accomplished, send response to: {clientAddress}.')
    
    # If there is a file to send back
    if returned is not None:
        returned = f'{fileName} {returned}'
        serverSocket.sendto(returned.encode(), clientAddress)
    
    else:
        serverSocket.sendto('None'.encode(), clientAddress)
    
serverSocket.close()