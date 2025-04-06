import socket
import random

BUFFER_SIZE = 1024
SERVER_PORT = 1057
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class RDT:
    def __init__(self, sockets: socket.socket):
        self.socket = sockets
        self.clients = {}
        self.timeout = 1
        self.socket.settimeout(self.timeout)
        print('RDT initialized. Timeout set to', self.timeout)

    def packet_loss(self) -> bool:
        return random.random() < 0.3

    def is_expected_bit(self, bit: bytes, addr: tuple) -> bool:
        return bit == str(self.clients[addr]['expected_bit']).encode()

    def is_ack_bit(self, bit: bytes) -> bool:
        return bit == b'1'

    def update_expected_bit(self, addr: tuple) -> None:
        self.clients[addr]['expected_bit'] = 1 - self.clients[addr]['expected_bit']
        print(f"Expected bit for {addr} updated to:", self.clients[addr]['expected_bit'])

    def update_last_packet(self, addr: tuple, message: bytes) -> None:
        self.clients[addr]['last_packet'] = message
        print(f'Last packet for {addr} updated.')

    def make_pkt(self, ack_bit: int, data: bytes, addr: tuple) -> bytes:
        return b' '.join([str(ack_bit).encode(), str(self.clients[addr]['expected_bit']).encode(), data])

    def get_header(self, message: bytes) -> tuple:
        return message.split(b' ', 2)  # ack, bit, data

    def send_ack(self, addr: tuple) -> None:
        ack_pkt = self.make_pkt(1, b'', addr)
        if not self.packet_loss():
            self.socket.sendto(ack_pkt, addr)
            print(f"ACK {self.clients[addr]['expected_bit']} sent to {addr}.")
        else:
            print(f"ACK {self.clients[addr]['expected_bit']} lost (simulated).")

    def rcv_pkt(self) -> tuple:
        """Loop que escuta e trata pacotes indefinidamente."""
        print("Servidor aguardando pacotes...\n")
        while True:
            try:
                message, addr = self.socket.recvfrom(BUFFER_SIZE)
                rcv_ack, rcv_bit, rcv_data = self.get_header(message)

                # Registra novo cliente
                if addr not in self.clients:
                    self.clients[addr] = {'expected_bit': rcv_bit, 'last_packet': message}
                    print(f"Novo cliente registrado: {addr}")
                    return rcv_data, addr

                # Verifica se é um ACK
                if self.is_ack_bit(rcv_ack):
                    print(f"Recebido ACK {rcv_bit} de {addr}.")
                    if self.clients[addr]['expected_bit'] == int(rcv_bit.decode()):
                        self.update_expected_bit(addr)
                    else:
                        continue  # O servidor não precisa fazer nada com ACKs aqui
                        
                else:
                    # Pacote duplicado
                    if message == self.clients[addr]['last_packet']:
                        print(f"Pacote duplicado de {addr}. Reenviando ACK {1 - self.clients[addr]['expected_bit']}.")
                        self.update_expected_bit(addr)
                        self.send_ack(addr)
                        continue

                    # Pacote esperado
                    elif self.is_expected_bit(rcv_bit, addr):
                        print(f"Pacote {rcv_bit.decode()} recebido corretamente de {addr}. Conteúdo: {rcv_data.decode()}")
                        self.send_ack(addr)
                        self.update_last_packet(addr, message)
                        self.update_expected_bit(addr)
                        return rcv_data, addr
                        # Aqui você pode processar o dado (ex: comando recebido)
                        # Ex: self.process_command(rcv_data.decode(), addr)
                    else:
                        print(f"Pacote fora de ordem de {addr}. Esperado: {self.clients[addr]['expected_bit']}. Reenviando ACK.")
                        self.send_ack(addr)

            except socket.timeout:
                continue  # Mantém o loop rodando eternamente

