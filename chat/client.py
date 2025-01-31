from socket import *
from threading import *

serverName = 'localhost'  # IP do servidor
serverPort = 1057
serverAddress = (serverName, serverPort)

clientSocket = socket(AF_INET, SOCK_DGRAM)

# Mensagem para conectar ao servidor
clientSocket.sendto('connect'.encode(), serverAddress)

def send_messages():
    """Função para enviar mensagens ao servidor"""
    while True:
        message = input()
        clientSocket.sendto(message.encode(), serverAddress)
        if message == "disconnect":
            break


def receive_messages():
    """Função para receber mensagens do servidor"""
    while True:
        try:
            receivedMessage, server = clientSocket.recvfrom(2048)
            print(receivedMessage.decode())
        except:
            break


# Criar threads para envio e recepção de mensagens
send_thread = Thread(target=send_messages)
receive_thread = Thread(target=receive_messages)

# Iniciar threads
send_thread.start()
receive_thread.start()

# Aguardar o término da thread de envio
send_thread.join()

# Enviar mensagem de desconexão e fechar o socket
clientSocket.sendto("disconnect".encode(), serverAddress)
clientSocket.close()
