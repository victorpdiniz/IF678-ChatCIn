import socket
import random
import threading
import queue

# Constants
BUFFER_SIZE = 1024
SERVER_PORT = 1057
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class Client:
    def __init__(self):
        """Inicializa o socket do cliente e parâmetros do RDT."""
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.client_socket.bind(('', 0))  # Porta aleatória
        self.expected_bit = 0
        self.last_packet_received = None
        self.timeout = 1
        self.client_socket.settimeout(None)

        self.login_status = False
        self.ack_queue = queue.Queue()   # Fila para armazenar ACKs recebidos
        self.data_queue = queue.Queue()  # Fila para armazenar pacotes de dados recebidos
        self.running = True

        print('Client iniciado com RDT 3.0 confiável.')
        print(f'Socket ligado na porta {self.client_socket.getsockname()[1]}')

    def packet_loss(self) -> bool:
        # Simula perda de pacote; valor negativo significa nunca perder (debug garantido)
        return random.random() < -1

    def is_duplicated(self, data: bytes) -> bool:
        return data == self.last_packet_received

    def is_expected_bit(self, bit: bytes) -> bool:
        return bit == str(self.expected_bit).encode()

    def is_ack_bit(self, bit: bytes) -> bool:
        return bit == b'1'

    def update_expected_bit(self) -> None:
        self.expected_bit = 1 - self.expected_bit

    def make_pkt(self, ack_bit: int, data: bytes) -> bytes:
        # Formato: ack_bit expected_bit dados
        pkt = b' '.join([str(ack_bit).encode(), str(self.expected_bit).encode(), data])
        return pkt

    def get_header(self, message: bytes) -> tuple:
        return message.split(b' ', 2)  # ack, bit, data
    
    def send_command(self, command):
        """Envia um comando para o servidor e aguarda resposta."""  
        self.send_pkt(command.encode(), SERVER_ADDRESS)
        
    def chat_friend(self, friend_name, message):
        """Envia mensagem privada para um amigo."""  ### (Novo)
        self.send_command(f'chat_friend {friend_name} {message}')
        
    def chat_group(self, group_name, key, message):
        """Envia mensagem para um grupo."""  ### (Novo)
        self.send_command(f'chat_group {group_name} {key} {message}')
        
    def login(self, username):
        """Solicita login no servidor."""  ### (Novo)
        self.send_command(f'login {username}')
        self.login_status = True
    
    def follow(self, friend):
        self.send_command(f'follow {friend}')

    def unfollow(self, friend):
        self.send_command(f'unfollow {friend}')

    def list_cinners(self):
        """Lista usuários online."""
        self.send_command('list:cinners')
        
    def list_friends(self):
        self.send_command('list:friends')
    
    def list_groups(self):
        self.send_command('list:groups')
    
    def list_mygroups(self):
        self.send_command('list:mygroups')
    
    def join_group(self, name, key):
        self.send_command(f'join {name} {key}')
    
    def logout(self):
        """Sai do servidor."""  ### (Novo)
        self.send_command('logout')
        self.login_status = False

    def leave_group(self, name):
        self.send_command(f'leave {name}')

    def create_group(self, name, key):
        self.send_command(f'create_group {name} {key}') 

    def ban(self, group, name):   
        self.send_command(f'ban {group} {name}')

    def delete_group(self, group):
        self.send_command(f'delete_group {group}')

    def send_pkt(self, data: bytes, addr: tuple) -> None:
        """Envia um pacote com bit de dados."""
        sndpkt = self.make_pkt(0, data)

        if not self.packet_loss():
            self.client_socket.sendto(sndpkt, addr)
            # print(f"[DEBUG] Pacote {self.expected_bit} enviado para {addr}")
        else:
            print(f'[DEBUG] Pacote {self.expected_bit} perdido (simulado).')

        self.rcv_ack(data)

    def send_ack(self, addr: tuple) -> None:
        """Envia um ACK ao servidor."""
        sndpkt = self.make_pkt(1, b'')
        self.client_socket.sendto(sndpkt, addr)
        self.update_expected_bit()

    def listen(self):
        """Thread que escuta o socket e separa mensagens em filas apropriadas."""
        # print("Thread de escuta iniciada...\n")
        while self.running:
            try:
                message, addr = self.client_socket.recvfrom(BUFFER_SIZE)
                rcv_ack, rcv_bit, rcv_data = self.get_header(message)

                if self.is_ack_bit(rcv_ack):
                    # print(f"[DEBUG] ACK recebido de {addr} com bit {rcv_bit}")
                    self.ack_queue.put((rcv_bit, addr))
                else:
                    # print(f"[DEBUG] Dados recebidos de {addr}: {rcv_data}")
                    self.data_queue.put((rcv_bit, rcv_data, addr))
                    self.rcv_packet()

            except socket.timeout:
                continue

    def rcv_packet(self) -> None:
        """Recebe pacotes e processa ACKs."""
        try:
            rcv_bit, rcv_data, addr = self.data_queue.get(timeout=1)
            # print(f"[DEBUG] Processando pacote de {addr} com bit {rcv_bit} e dados: {rcv_data}")
            self.send_ack(addr)
            self.last_packet_received = rcv_data
            print(f"{rcv_data.decode()}")
        except queue.Empty:
            pass
            # print("[DEBUG] Nenhum pacote disponível na fila de dados (timeout).")

    def rcv_ack(self, data: bytes) -> None:
        """Aguarda e processa ACKs da fila."""
        while True:
            try:
                rcv_bit, addr = self.ack_queue.get(timeout=1)
                #print(f"[DEBUG] ACK com bit {rcv_bit} recebido de {addr}")

                if self.is_expected_bit(rcv_bit):
                    #print(f"[DEBUG] ACK esperado recebido. Atualizando bit e continuando.")
                    self.update_expected_bit()
                    return
                else:
                    ##print(f"[DEBUG] ACK fora de ordem. Reenviando pacote.")
                    self.send_pkt(data, addr)
                    return

            except queue.Empty:
                #print("[DEBUG] Timeout esperando ACK. Reenviando pacote.")
                self.send_pkt(data, SERVER_ADDRESS)
                return

    def run(self):
        """Loop principal do cliente."""
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

        # print("Digite mensagens para enviar ao servidor. Digite 'bye' para sair.")
        while self.running:
            if(self.login_status):
                print('Comandos disponíveis:')
                print('  logout')
                print('  follow <friend>')
                print('  unfollow <friend>')
                print('  list:friends (Lista amigos)')
                print('  list:cinners (Lista usuários online)')
                print('  list:groups')
                print('  list:mygroups')
                print('  create_group <nome> <chave>')
                print('  chat_friend <nome_amigo> <mensagem>')
                print('  chat_group <grupo> <chave> <mensagem>')
                print('  join_group <grupo> <chave>')
                print('  leave_group <grupo>')
                print('  delete_group <grupo>')
                command = input('Digite um comando: ').strip()
                
                if command.startswith('chat_friend'):
                    _, friend, *msg = command.split()
                    self.chat_friend(friend, " ".join(msg))

                elif command.startswith('chat_group'):
                    _, group, key, *msg = command.split()
                    self.chat_group(group, key, " ".join(msg))

                elif command.startswith('follow'):
                    _, friend = command.split(' ')
                    self.follow(friend)
                
                elif command.startswith('unfollow'):
                    _, friend = command.split(' ')
                    self.unfollow(friend) 
                
                elif command.startswith('create_group'):
                    _, name, key = command.split(' ')
                    self.create_group(name, key) 
                
                elif command.startswith('join'):
                    _, name, key = command.split(' ')
                    self.join_group(name, key)
                
                elif command.startswith('logout'):
                    self.logout()

                elif command.startswith('list:friends'):
                    self.list_friends()
                
                elif command =='list:cinners':
                    self.list_cinners()
                    
                elif command =='list:groups':
                    self.list_groups()
                
                elif command =='list:mygroups':
                    self.list_mygroups()
                
                elif command =='leave_group':
                    _, name = command.split(' ')
                    self.leave_group(name)
                
                elif command.startswith('ban'):
                    _, group, name = command.split(' ')
                    self.ban(group, name)

                elif command.startswith('delete_group'):
                    _, group = command.split(' ')
                    self.delete_group(group) 

                else:
                    print('Comando inválido. Tente novamente.')
        
            else:
                print('Comandos disponíveis:')
                print('  login <username>')
                command = input('Digite um comando: ').strip()
                if command.startswith('login'):
                    _,username = command.split()
                    self.login(username)
                else:
                    print('Comando inválido. Tente novamente.')

        self.client_socket.close()


if __name__ == '__main__':
    client = Client()
    client.run()
