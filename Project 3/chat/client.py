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
        self.rdt = RDT(self.client_socket) 
        self.login_status = False 
        print('Cliente pronto.')

    def send_command(self, command):
        """Envia um comando para o servidor e aguarda resposta."""  
        self.rdt.send_pkt(command.encode(), SERVER_ADDRESS)
            
        response = self.rdt.rcv_packet()
        response=response[0].decode()
        return response
    
    def chat_friend(self, friend_name, message):
        """Envia mensagem privada para um amigo."""  ### (Novo)
        self.send_command(f'chat_friend {friend_name} {message}')
    
    def chat_group(self, group_name, key, message):
        """Envia mensagem para um grupo."""  ### (Novo)
        self.send_command(f'chat_group {group_name} {key} {message}')
    
    def login(self, username):
        """Solicita login no servidor."""  ### (Novo)
        response = self.send_command(f'login {username}')
        if response == 'Nome já em uso.':
            print(response)
        else:
            print(response)
            self.login_status = True
    
    def list_cinners(self):
        """Lista usuários online."""
        response = self.send_command('list:cinners')
        print(response)
            
    def logout(self):
        """Sai do servidor."""  ### (Novo)
        response = self.send_command('logout')
        print(response)
        self.login_status = False

    def run(self):
        """Loop do cliente para entrada do usuário."""
        
        if(self.login_status):
            print('Comandos disponíveis:')
            print('  logout')
            print('  list:cinners (Lista usuários online)')
            print('  create_group <nome> <chave>')
            print('  chat_friend <nome_amigo> <mensagem>')
            print('  chat_group <grupo> <chave> <mensagem>')
            print('  close (Encerra conexão)')
        else:
            print('Comandos disponíveis:')
            print('  login <username>')
        
        while True:
            command = input('Digite um comando: ').strip()
            
            if(self.login_status):
                if command.startswith('chat_friend'):
                    _, friend, *msg = command.split()
                    self.chat_friend(friend, " ".join(msg))

                elif command.startswith('chat_group'):
                    _, group, key, *msg = command.split()
                    self.chat_group(group, key, " ".join(msg))

                elif command == 'logout':
                    self.logout()

                elif command =='list:cinners':
                    self.list_cinners()
                else:
                    print('Comando inválido. Tente novamente.')

            else:
                if command.startswith('login'):
                    _,username = command.split()
                    self.login(username)
                

                else:
                    print('Comando inválido. Tente novamente.')

        self.client_socket.close()

if __name__ == '__main__':
    client = Client()
    client.run()
