import socket
import random
import queue

BUFFER_SIZE = 1024
SERVER_PORT = 1057
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class RDT:
    def __init__(self, sockets: socket.socket):
        self.socket = sockets
        self.clients = {}
        self.timeout = 1
        self.ack_queue = queue.Queue()  # Fila para armazenar ACKs recebidos
        print('RDT initialized. Timeout set to', self.timeout)

    def packet_loss(self) -> bool:
        return random.random() < 0.3

    def is_expected_bit(self, bit: bytes, addr: tuple) -> bool:
        return bit == str(self.clients[addr]['expected_bit']).encode()

    def is_ack_bit(self, bit: bytes) -> bool:
        return bit == b'1'

    def update_expected_bit(self, addr: tuple) -> None:
        self.clients[addr]['expected_bit'] = 1 - self.clients[addr]['expected_bit']
        # print(f"Expected bit for {addr} updated to:", self.clients[addr]['expected_bit'])

    def update_last_packet(self, addr: tuple, message: bytes) -> None:
        self.clients[addr]['last_packet'] = message
        # print(f'Last packet for {addr} updated.')

    def make_pkt(self, ack_bit: int, data: bytes, addr: tuple) -> bytes:
        return b' '.join([str(ack_bit).encode(), str(self.clients[addr]['expected_bit']).encode(), data])

    def get_header(self, message: bytes) -> tuple:
        return message.split(b' ', 2)  # ack, bit, data

    def send_ack(self, addr: tuple) -> None:
        ack_pkt = self.make_pkt(1, b'', addr)
        # if not self.packet_loss():
        self.socket.sendto(ack_pkt, addr)
        # print(f"ACK {self.clients[addr]['expected_bit']} sent to {addr}.")
        # else:
        #     print(f"ACK {self.clients[addr]['expected_bit']} lost (simulated).")
        self.update_expected_bit(addr)


    def send_pkt(self, data: bytes, addr: tuple) -> None:
        pkt = self.make_pkt(0, data, addr)

        while True:
            if not self.packet_loss():
                self.socket.sendto(pkt, addr)
                #print(f"Packet sent to {addr}.")
            else:
                print(f"Packet lost (simulated) when sending to {addr}.")
            self.socket.settimeout(self.timeout)
            try:
                # Espera pelo ACK correspondente na fila
                data, address = self.socket.recvfrom(BUFFER_SIZE)
                is_ack, rcv_bit, _ = self.get_header(data)

                if int(rcv_bit.decode()) == self.clients[addr]['expected_bit']:
                    #print(f"ACK {rcv_bit} recebido corretamente.")
                    self.update_expected_bit(addr)
                    break
                else:
                    print(f"ACK {rcv_bit} fora de ordem, reenviando...")

            except socket.timeout:
                # print(f"Timeout Aguardando ACK {self.clients[addr]['expected_bit']} de {addr}, retransmitindo...")
                continue

    def rcv_pkt(self) -> tuple:
        """Loop que escuta e trata pacotes indefinidamente."""
        #print("Servidor aguardando pacotes...\n")
        self.socket.settimeout(None)
        while True:
            message, addr = self.socket.recvfrom(BUFFER_SIZE)
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            #print(message)

            # Registra novo cliente
            if addr not in self.clients:
                self.clients[addr] = {'expected_bit': int(rcv_bit), 'last_packet': message}
                print(f"Novo cliente registrado: {addr}")
                self.send_ack(addr)
                return rcv_data, addr

            # É um ACK?
            if self.is_ack_bit(rcv_ack):
                #print(f"Recebido ACK {rcv_bit} de {addr}.")
                self.ack_queue.put(int(rcv_bit))  # Armazena o ACK para send_pkt
                continue

            # Pacote duplicado
            if message == self.clients[addr]['last_packet']:
                #print(f"Pacote duplicado de {addr}. Reenviando ACK.")
                self.update_expected_bit(addr)
                self.send_ack(addr)
                continue

            # Pacote esperado
            if self.is_expected_bit(rcv_bit, addr):
                #print(f"Pacote {rcv_bit.decode()} recebido corretamente de {addr}. Conteúdo: {rcv_data.decode()}")
                self.send_ack(addr)
                self.update_last_packet(addr, message)
                return rcv_data, addr
            else:
                continue

