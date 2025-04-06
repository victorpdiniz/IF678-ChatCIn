from socket import socket, AF_INET, SOCK_DGRAM
from rdt import RDT
from database import Database
from utils import parse_command

SERVER_PORT = 1057
SERVER_ADDRESS = ('localhost', SERVER_PORT)

class Server:
    def __init__(self):
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        self.rdt = RDT(self.server_socket)
        self.db = Database()
        print('Servidor iniciado.')

    def handle_request(self, message, addr):
        """Lida com comandos do cliente."""
        command, args = parse_command(message)
        command=command.decode()
        user_name = self.get_user_by_addr(addr)
        if command == "login":
            args[0] = args[0].decode()
            if self.db.add_user(args[0], addr):
                self.rdt.send_pkt(f"Bem-vindo, {args[0]}!".encode(), addr)
            else:
                self.rdt.send_pkt("Nome já em uso.".encode(), addr)

        elif command == "logout":
            if user_name:
                self.db.remove_user(user_name)
                self.rdt.send_pkt("Você saiu do chat.".encode(), addr)

        elif command == "list:cinners":
            users = self.db.get_online_users()
            decoded_users = [u.decode() if isinstance(u, bytes) else u for u in users]
            msg = ", ".join(decoded_users)
            self.rdt.send_pkt(msg.encode(), addr)

        elif command == "create_group":
            if len(args) < 2:
                self.rdt.send_pkt("Uso: create_group <nome> <chave>".encode(), addr)
                return
            group_name, group_key = args
            if self.db.create_group(group_name, group_key, user_name):
                self.rdt.send_pkt(f"Grupo {group_name} criado!".encode(), addr)
            else:
                self.rdt.send_pkt("Grupo já existe!".encode(), addr)

        elif command == "chat_friend":
            if len(args) < 2:
                self.rdt.send_pkt("Uso: chat_friend <nome_amigo> <mensagem>".encode(), addr)
                return
            friend_name, message_text = args[0], " ".join(args[1:])
            friend = self.db.users.get(friend_name)
            if friend:
                self.rdt.send_pkt(f"[{user_name}] {message_text}".encode(), friend.address)
            else:
                self.rdt.send_pkt("Amigo não encontrado.".encode(), addr)

        elif command == "chat_group":
            if len(args) < 3:
                self.rdt.send_pkt("Uso: chat_group <grupo> <chave> <mensagem>".encode(), addr)
                return
            group_name, key, message_text = args[0], args[1], " ".join(args[2:])
            group = self.db.groups.get(group_name)
            if group and group.key == key:
                for member in group.members:
                    if member != user_name:
                        self.rdt.send_pkt(f"[{user_name}@{group_name}] {message_text}".encode(), self.db.users[member].address)
            else:
                self.rdt.send_pkt("Grupo não encontrado ou chave incorreta.".encode(), addr)

    def get_user_by_addr(self, addr):
        """Retorna o nome do usuário pelo endereço."""
        for name, user in self.db.users.items():
            if user.address == addr:
                return name
        return None

    def run(self):
        """Loop do servidor."""
        while True:
            message, addr = self.rdt.rcv_packet()#aqui está retornando mais argumentos do que deveria
            self.handle_request(message, addr)

if __name__ == "__main__":
    server = Server()
    server.run()