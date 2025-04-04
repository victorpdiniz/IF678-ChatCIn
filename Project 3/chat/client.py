from socket import socket, AF_INET, SOCK_DGRAM
from rdt import RDT

# Constantes
SERVER_PORT = 1057
CLIENT_PORT = 1058
BUFFER_SIZE = 1024
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
CLIENT_ADDRESS = (HOST, CLIENT_PORT)

class Client:
    def __init__(self):
        """Inicializa o cliente e o socket."""
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.bind(CLIENT_ADDRESS)
        self.rdt = RDT(self.client_socket)  ### (Novo: Instância de RDT armazenada como atributo)
        print('Cliente pronto.')

    def send_command(self, command):
        """Envia um comando para o servidor e aguarda resposta."""  ### (Novo: Função genérica para envio de comandos)
        self.rdt.send_pkt(command.encode(), SERVER_ADDRESS)
        response = self.rdt.rcv_packet().decode()
        print(f'Servidor: {response}')
    
    def chat_friend(self, friend_name, message):
        """Envia mensagem privada para um amigo."""  ### (Novo)
        self.send_command(f'chat_friend {friend_name} {message}')
    
    def chat_group(self, group_name, key, message):
        """Envia mensagem para um grupo."""  ### (Novo)
        self.send_command(f'chat_group {group_name} {key} {message}')
    
    def login(self, username):
        """Solicita login no servidor."""  ### (Novo)
        self.send_command(f'login {username}')
    
    def logout(self):
        """Sai do servidor."""  ### (Novo)
        self.send_command('logout')

    def run(self):
        """Loop do cliente para entrada do usuário."""
        print('Comandos disponíveis:')
        print('  login <username>')
        print('  logout')
        print('  list:cinners (Lista usuários online)')
        print('  create_group <nome> <chave>')
        print('  chat_friend <nome_amigo> <mensagem>')
        print('  chat_group <grupo> <chave> <mensagem>')
        print('  close (Encerra conexão)')

        while True:
            command = input('Digite um comando: ').strip()
            
            if command.startswith('chat_friend'):
                _, friend, *msg = command.split()
                self.chat_friend(friend, " ".join(msg))

            elif command.startswith('chat_group'):
                _, group, key, *msg = command.split()
                self.chat_group(group, key, " ".join(msg))

            elif command.startswith('login'):
                _,username = command.split()
            
                self.login(username)

            elif command == 'logout':
                self.logout()

            elif command == 'close':
                self.send_command('close')
                break

            else:
                self.send_command(command)  ### (Novo: Agora envia qualquer comando diretamente)

        self.client_socket.close()

if __name__ == '__main__':
    client = Client()
    client.run()
