import socket
import random
from utils import parse_command
from database import Database
from users_groups import User, Group


# Constantes de configuração do servidor
BUFFER_SIZE = 1024
SERVER_PORT = 1057
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class Server:
    def __init__(self):
        """Inicializa o socket do servidor, banco de dados e estrutura para armazenar clientes."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        self.clients = {}  # Dicionário para armazenar estado de cada cliente
        self.timeout = 1
        self.server_socket.settimeout(None)
        self.db = Database()
        print("Servidor pronto e aguardando conexões...")

    def packet_loss(self) -> bool:
        """Simula perda de pacote (atualmente desativada com < 0)."""
        return random.random() < -1

    def make_pkt(self, ack_bit: int, data: bytes, addr: tuple) -> bytes:
        """Monta um pacote com bit de ACK, expected_bit e dados."""
        # print(f"[DEBUG] Montando pacote: ack_bit={ack_bit}, expected_bit={self.clients[addr]['expected_bit']}, data={data}")
        return b' '.join([
            str(ack_bit).encode(),
            str(self.clients[addr]['expected_bit']).encode(),
            data
        ])

    def get_header(self, message: bytes) -> tuple:
        """Extrai o cabeçalho do pacote: ack_bit, expected_bit, e os dados."""
        return message.split(b' ', 2)

    def update_expected_bit(self, addr: tuple) -> None:
        """Alterna o expected_bit do cliente (0 → 1 ou 1 → 0)."""
        # print(f"[DEBUG] Alternando expected_bit para {1 - self.clients[addr]['expected_bit']} para {addr}")
        self.clients[addr]['expected_bit'] = 1 - self.clients[addr]['expected_bit']

    def update_last_packet(self, addr: tuple, message: bytes) -> None:
        """Atualiza o último pacote recebido de um cliente."""
        # print(f"[DEBUG] Atualizando último pacote de {addr}")
        self.clients[addr]['last_packet'] = message

    def is_expected_bit(self, bit: bytes, addr: tuple) -> bool:
        """Verifica se o bit recebido é o esperado para o cliente."""
        return bit == str(self.clients[addr]['expected_bit']).encode()

    def is_ack_bit(self, bit: bytes) -> bool:
        """Verifica se o bit representa um ACK (bit = 1)."""
        return bit == b'1'

    def send_ack(self, addr: tuple) -> None:
        """Envia pacote de ACK para o cliente e atualiza expected_bit."""
        ack_pkt = self.make_pkt(1, b'', addr)
        # print(f"[DEBUG] Enviando ACK para {addr}")
        self.server_socket.sendto(ack_pkt, addr)
        self.update_expected_bit(addr)

    def send_pkt(self, data: bytes, addr: tuple) -> None:
        """Envia pacote com tratamento de perda e espera de ACK do cliente."""
        pkt = self.make_pkt(0, data, addr)
        while True:
            if not self.packet_loss():
                # print(f"[DEBUG] Enviando pacote para {addr}: {pkt}")
                self.server_socket.sendto(pkt, addr)
            # else:
            #     print(f"[DEBUG] Simulando perda de pacote para {addr}.")

            try:
                ack_data, _ = self.server_socket.recvfrom(BUFFER_SIZE)
                is_ack, rcv_bit, _ = self.get_header(ack_data)
                # print(f"[DEBUG] ACK recebido de {addr}: bit={rcv_bit}")
                if int(rcv_bit.decode()) == self.clients[addr]['expected_bit']:
                    self.update_expected_bit(addr)
                    return
                # else:
                #     print(f"[DEBUG] ACK fora de ordem ({rcv_bit}) de {addr}, reenviando pacote...")
            except socket.timeout:
                # print(f"[DEBUG] Timeout esperando ACK de {addr}, reenviando pacote...")
                continue

    def rcv_pkt(self) -> tuple:
        """Recebe pacotes, trata novos clientes, duplicatas e responde com ACKs."""
        while True:
            message, addr = self.server_socket.recvfrom(BUFFER_SIZE)
            # print(f"[DEBUG] Pacote recebido de {addr}: {message}")
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)

            if addr not in self.clients:
                # print(f"[DEBUG] Registrando novo cliente: {addr}")
                self.clients[addr] = {
                    'expected_bit': int(rcv_bit),
                    'last_packet': message
                }
                self.send_ack(addr)
                return rcv_data, addr

            if self.is_ack_bit(rcv_ack):
                # print(f"[DEBUG] Pacote é um ACK de {addr}, ignorando...")
                continue

            if message == self.clients[addr]['last_packet'] and not self.is_expected_bit(rcv_bit, addr):
                # print(f"[DEBUG] Pacote duplicado de {addr}, reenviando ACK...")
                self.send_ack(addr)
                continue

            if self.is_expected_bit(rcv_bit, addr):
                # print(f"[DEBUG] Pacote esperado de {addr}, processando...")
                self.send_ack(addr)
                self.update_last_packet(addr, message)
                return rcv_data, addr

    def handle_request(self, message, addr):
        """Lida com comandos do cliente."""
        command, args = parse_command(message)
        command = command.decode()
        user_name = self.db.get_user_by_address(addr)

        if command == "login":#ok!
            args[0] = args[0].decode()
            if self.db.add_user(args[0], addr):
                self.send_pkt(f"Bem-vindo, {args[0]}!".encode(), addr)
            else:
                self.send_pkt("Nome já em uso.".encode(), addr)

        elif command == "logout":#ok!
            if user_name:
                self.db.remove_user(user_name)
                self.send_pkt(f"Você saiu do chat {user_name}.".encode(), addr)

        elif command == "list:cinners":#ok!
            users = self.db.get_online_users()
            decoded_users = [u.decode() if isinstance(u, bytes) else u for u in users]
            msg = ", ".join(decoded_users)
            self.send_pkt(msg.encode(), addr)

        elif command == "create_group":#ok!
            group_name, group_key= args[0].decode(), args[1].decode()
            if self.db.create_group(group_name, group_key, user_name):
                self.send_pkt(f"Grupo {group_name} criado!".encode(), addr)
            else:
                self.send_pkt("Grupo já existe!".encode(), addr)
                
        elif command == "delete_group":# +- ok!
            group_name = args[0].decode()
            if self.db.delete_group(group_name, user_name):
                self.send_pkt(f"Grupo {group_name} deletado!".encode(), addr)
            else:
                self.send_pkt("Grupo não foi deletado!".encode(), addr)

        
        elif command == "chat_friend": #não ok!
            friend_name = args[0].decode()
            msg = b' '.join(args[1:]).decode()
            friend_address = self.db.users[friend_name].address
            friends = self.db.get_friends(user_name)
            decoded_users = [u.decode() if isinstance(u, bytes) else u for u in friends]
            if friend_name in decoded_users:
                message = f"[{str(user_name.name)}/{user_name.address[0]}:{user_name.address[1]}]{msg}"
                self.send_pkt(message.encode(), friend_address)
            else:
                self.send_pkt("Amigo não encontrado".encode(), addr)
            
        elif command == "chat_group":
            group_name, key, msg = args[0].decode(), args[1].decode(), b" ".join(args[2:])
            group = self.db.groups.get(group_name)
            print(group)
            if group and group.key == key:
                # print(f"[DEBUG] Enviando mensagem de {user_name} para grupo {group_name}")
                if user_name.name != group.admin:
                    message = f"[{str(user_name.name)}/{user_name.address[0]}:{user_name.address[1]}]{msg.decode()}"
                    self.send_pkt(message.encode(), self.db.users[group.admin].address)
                for member in group.members:
                    if member != user_name.name:
                        print(member)
                        message = f"[{str(user_name.name)}/{user_name.address[0]}:{user_name.address[1]}]{msg.decode()}"
                        self.send_pkt(message.encode(), self.db.users[member.name].address)
            else:
                self.send_pkt("Grupo não encontrado ou chave incorreta.".encode(), addr)
        
        elif command == "follow":#ok!
            friend_name = args[0].decode()
            if self.db.add_friend(friend_name, addr):
                self.send_pkt(f"Amigo {friend_name} adicionado com sucesso.".encode(), addr)
            else:
                self.send_pkt(f"Amigo já adicionado.".encode(), addr)
           
        elif command == "unfollow":#ok!
            friend_name = args[0].decode()
            if self.db.remove_friend(friend_name, addr):
                self.send_pkt(f"Amigo {friend_name} removido com sucesso.".encode(), addr)
            else:
                self.send_pkt(f"Amigo já removido.".encode(), addr)
        
        elif command=="list:friends":#ok!
            friends = self.db.get_friends(user_name)
            decoded_users = [u.decode() if isinstance(u, bytes) else u for u in friends]
            msg = ", ".join(decoded_users)
            self.send_pkt(msg.encode(), addr)
            
        elif command=="list:groups":#ok!
            groups = self.db.get_groups(user_name)
            print(groups)
            decoded_groups = [u.decode() if isinstance(u, bytes) else u for u in groups]
            msg = ", ".join(decoded_groups)
            self.send_pkt(msg.encode(), addr)
            
        elif command=="list:mygroups":#ok!
            groups = self.db.get_mygroups(user_name)
            print(groups)
            decoded_groups = [u.decode() if isinstance(u, bytes) else u for u in groups]
            msg = ", ".join(decoded_groups)
            self.send_pkt(msg.encode(), addr)
        
        elif command == "join":#ok!
            group_name, group_key= args[0].decode(), args[1].decode()
            if self.db.add_user_to_group(group_name,group_key, user_name):
                self.send_pkt(f"Adicionado ao {group_name}!".encode(), addr)
            else:
                self.send_pkt("Grupo não existe!".encode(), addr)
                
        elif command == "leave":#ok!
            group_name = args[0].decode()
            if self.db.remove_user_from_group(group_name, user_name):
                self.send_pkt(f"Você saiu do grupo: {group_name}!".encode(), addr)
            else:
                self.send_pkt("Grupo não existe!".encode(), addr)

    def run(self):
        """Loop principal do servidor."""
        try:
            while True:
                data, sender = self.rcv_pkt()
                # print(f"Mensagem recebida de {sender}: {data.decode()}")
                self.handle_request(data, sender)

        except KeyboardInterrupt:
            print("\nServidor encerrado.")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = Server()
    server.run()
