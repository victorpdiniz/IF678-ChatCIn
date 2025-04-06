import socket
import random
from utils import parse_command
from database import Database
from users_groups import User, Group

# Constantes
BUFFER_SIZE = 1024
SERVER_PORT = 1057
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class Server:
    def __init__(self):
        """Inicializa o socket e estruturas para clientes."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        self.clients = {}  # Armazena o expected_bit e último pacote de cada cliente
        self.timeout = 1
        self.db = Database()
        print("Servidor pronto e aguardando conexões...")

    def packet_loss(self) -> bool:
        return random.random() < -1

    def make_pkt(self, ack_bit: int, data: bytes, addr: tuple) -> bytes:
        return b' '.join([
            str(ack_bit).encode(),
            str(self.clients[addr]['expected_bit']).encode(),
            data
        ])

    def get_header(self, message: bytes) -> tuple:
        return message.split(b' ', 2)

    def update_expected_bit(self, addr: tuple) -> None:
        self.clients[addr]['expected_bit'] = 1 - self.clients[addr]['expected_bit']

    def update_last_packet(self, addr: tuple, message: bytes) -> None:
        self.clients[addr]['last_packet'] = message

    def is_expected_bit(self, bit: bytes, addr: tuple) -> bool:
        return bit == str(self.clients[addr]['expected_bit']).encode()

    def is_ack_bit(self, bit: bytes) -> bool:
        return bit == b'1'

    def send_ack(self, addr: tuple) -> None:
        ack_pkt = self.make_pkt(1, b'', addr)
        self.server_socket.sendto(ack_pkt, addr)
        self.update_expected_bit(addr)

    def send_pkt(self, data: bytes, addr: tuple) -> None:
        pkt = self.make_pkt(0, data, addr)
        while True:
            if not self.packet_loss():
                self.server_socket.sendto(pkt, addr)
            else:
                print(f"Simulando perda de pacote para {addr}.")

            self.server_socket.settimeout(self.timeout)
            try:
                ack_data, _ = self.server_socket.recvfrom(BUFFER_SIZE)
                is_ack, rcv_bit, _ = self.get_header(ack_data)
                if int(rcv_bit.decode()) == self.clients[addr]['expected_bit']:
                    self.update_expected_bit(addr)
                    return
                else:
                    print(f"ACK fora de ordem ({rcv_bit}) recebido de {addr}, reenviando...")
            except socket.timeout:
                continue

    def rcv_pkt(self) -> tuple:
        """Espera por pacotes e processa duplicatas, ACKs e novos dados."""
        while True:
            message, addr = self.server_socket.recvfrom(BUFFER_SIZE)
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)

            # Novo cliente
            if addr not in self.clients:
                self.clients[addr] = {
                    'expected_bit': int(rcv_bit),
                    'last_packet': message
                }
                print(f"Novo cliente registrado: {addr}")
                self.send_ack(addr)
                return rcv_data, addr

            # Se for ACK, ignora aqui (ack tratado no envio)
            if self.is_ack_bit(rcv_ack):
                continue

            # Pacote duplicado
            if message == self.clients[addr]['last_packet']:
                print(f"Pacote duplicado de {addr}, reenviando ACK.")
                self.send_ack(addr)
                continue

            # Pacote esperado
            if self.is_expected_bit(rcv_bit, addr):
                self.send_ack(addr)
                self.update_last_packet(addr, message)
                return rcv_data, addr

    def handle_request(self, message, addr):
        """Lida com comandos do cliente."""
        command, args = parse_command(message)
        command=command.decode()
        user_name = self.db.get_user_by_address(addr)

        if command == "login":
            args[0] = args[0].decode()
            if self.db.add_user(args[0], addr):
                self.send_pkt(f"Bem-vindo, {args[0]}!".encode(), addr)
            else:
                self.send_pkt("Nome já em uso.".encode(), addr)

        elif command == "logout":
            if user_name:
                self.db.remove_user(user_name)
                self.send_pkt("Você saiu do chat.".encode(), addr)

        elif command == "list:cinners":
            users = self.db.get_online_users()
            decoded_users = [u.decode() if isinstance(u, bytes) else u for u in users]
            msg = ", ".join(decoded_users)
            self.send_pkt(msg.encode(), addr)

        elif command == "create_group":
            if len(args) < 2:
                self.send_pkt("Uso: create_group <nome> <chave>".encode(), addr)
                return
            group_name, group_key = args
            if self.db.create_group(group_name, group_key, user_name):
                self.send_pkt(f"Grupo {group_name} criado!".encode(), addr)
            else:
                self.send_pkt("Grupo já existe!".encode(), addr)

        elif command == "chat_friend":
            if len(args) < 2:
                self.send_pkt("Uso: chat_friend <nome_amigo> <mensagem>".encode(), addr)
                return
            friend_name, message_text = args[0], " ".join(args[1:])
            friend = self.db.users.get(friend_name)
            if friend:
                self.send_pkt(f"[{user_name}] {message_text}".encode(), friend.address)
            else:
                self.send_pkt("Amigo não encontrado.".encode(), addr)

        elif command == "chat_group":
            if len(args) < 3:
                self.send_pkt("Uso: chat_group <grupo> <chave> <mensagem>".encode(), addr)
                return
            group_name, key, message_text = args[0], args[1], " ".join(args[2:])
            group = self.db.groups.get(group_name)
            member = group.get(user_name)
            if group and group.key == key and member:
                for member in group.members:
                    if member != user_name:
                        self.send_pkt(f"[{user_name}@{group_name}] {message_text}".encode(), self.db.users[member].address)
            else:
                self.send_pkt("Grupo não encontrado ou chave incorreta.".encode(), addr)       
            
    def broadcast(self, message: bytes, sender: tuple):
        """Envia a mensagem para todos os clientes, exceto o remetente."""
        for addr in self.clients:
            if addr != sender:
                #[<nome_do_usuário>/<IP>:<SOCKET>]<mensagem>. 
                # message = 
                self.send_pkt(message, addr)

    def run(self):
        """Loop principal do servidor."""
        try:
            while True:
                data, sender = self.rcv_pkt()
                print(f"Mensagem recebida de {sender}: {data.decode()}")

                self.handle_request(data, sender)

        except KeyboardInterrupt:
            print("\nServidor encerrado.")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    server = Server()
    server.run()
