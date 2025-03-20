from socket import *

serverPort = 1057
host = 'localhost'  # Escuta em todas as interfaces
serverAddress = (host, serverPort)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)

print(f'The server is ready to receive messages at port {serverPort}.')
clients = {}  # Dicionario de clientes conectados

while True:
    # Receber mensagem de um cliente
    message, clientAddress = serverSocket.recvfrom(2048)
    decodedMessage = message.decode()
    # print(f'Message received from {clientAddress}: {decodedMessage}')

    if clientAddress not in clients:
        name = decodedMessage.split()[0]
        clients[name] = clientAddress
        print(f'{name} connected.')

    elif decodedMessage == 'disconnect':
        # Remover cliente da lista
        if clientAddress in clients:
            clients.pop(clients.popitem(clientAddress))
            print(f'{name} disconnected.')
        continue

    # Enviar a mensagem recebida para todos os clientes conectados
    for name, client in clients.items():
        if client != clientAddress:  # Não enviar a mensagem de volta para o remetente
            serverSocket.sendto(f'{name}: {decodedMessage}'.encode(), client)

    if decodedMessage == "close":
        break  # Encerra o servidor

serverSocket.close()
