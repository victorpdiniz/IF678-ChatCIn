import socket
import random
import threading
import queue

# Constants
BUFFER_SIZE = 1024
SERVER_PORT = 1057
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class RDT:
    def __init__(self, sockets: socket.socket):
        self.socket = sockets
        self.expected_bit = 0
        self.last_packet_received = None
        self.timeout = 1
        self.socket.settimeout(self.timeout)

        # Fila para ACKs e pacotes
        self.ack_queue = queue.Queue()
        self.data_queue = queue.Queue()

        print('RDT initialized with expected bit 0.')
        print(f'Timeout set to {self.timeout} seconds.')

    def packet_loss(self) -> bool:
        return random.random() < 0.3

    def is_duplicated(self, data: bytes) -> bool:
        return data == self.last_packet_received

    def is_expected_bit(self, bit: bytes) -> bool:
        return bit == str(self.expected_bit).encode()

    def is_ack_bit(self, bit: bytes) -> bool:
        return bit == b'1'

    def update_expected_bit(self) -> None:
        self.expected_bit = 1 - self.expected_bit
        # print('Expected bit updated to:', self.expected_bit)

    def make_pkt(self, ack_bit: int, data: bytes) -> bytes:
        return b' '.join([str(ack_bit).encode(), str(self.expected_bit).encode(), data])

    def get_header(self, message: bytes) -> tuple:
        return message.split(b' ', 2)  # ack, bit, data

    def send_pkt(self, data: bytes, addr: tuple) -> None:
        sndpkt = self.make_pkt(0, data)

        if not self.packet_loss():
            # print(f'Packet {self.expected_bit} sent.')
            self.socket.sendto(sndpkt, addr)
        else:
            print(f'Packet {self.expected_bit} lost.')

        # Aguarda ACK
        self.rcv_ack(data)

    def send_ack(self, addr: tuple) -> None:
        sndpkt = self.make_pkt(1, b'')
        self.socket.sendto(sndpkt, addr)
        # print(f'ACK {self.expected_bit} sent.')
        self.update_expected_bit()

    def listen(self):
        """Thread que escuta tudo o que chega e distribui nas filas."""
        print("Client listener started...\n")
        while True:
            try:
                message, addr = self.socket.recvfrom(BUFFER_SIZE)
                rcv_ack, rcv_bit, rcv_data = self.get_header(message)
                print(f'Received packet from {addr}: {message}')
                if self.is_ack_bit(rcv_ack):
                    self.ack_queue.put((rcv_bit, addr))
                else:
                    self.data_queue.put((rcv_bit, rcv_data, addr))
                    self.rcv_packet()

            except socket.timeout:
                continue

    def rcv_packet(self) -> bytes:
        """Espera por novos pacotes de dados (thread segura)."""
        while True:
            try:
                rcv_bit, rcv_data, addr = self.data_queue.get(timeout=1)
                if self.is_expected_bit(rcv_bit):
                    # print(f'Received packet {rcv_bit}.')
                    self.send_ack(addr)
                    self.last_packet_received = rcv_data
                    return rcv_data
                else:
                    # print(f'Received out-of-order packet {rcv_bit}. Expected {self.expected_bit}.')
                    self.send_ack(addr)

            except queue.Empty:
                continue

    def rcv_ack(self, data: bytes) -> None:
        """Espera por um ACK na fila."""
        while True:
            try:
                rcv_bit, addr = self.ack_queue.get(timeout=1)

                if self.is_expected_bit(rcv_bit):
                    # print(f'Received ACK {rcv_bit}.')
                    self.update_expected_bit()
                    return
                else:
                    # print(f'Received unexpected ACK {rcv_bit}. Resending packet.')
                    self.send_pkt(data, addr)
                    return

            except queue.Empty:
                # print(f'Timeout waiting for ACK {self.expected_bit}. Resending packet.')
                self.send_pkt(data, SERVER_ADDRESS)
                return
