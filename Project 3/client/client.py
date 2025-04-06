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
        self.client_socket.settimeout(self.timeout)

        self.ack_queue = queue.Queue()
        self.data_queue = queue.Queue()
        self.running = True

        print('Client iniciado com RDT 3.0 confiável.')
        print(f'Socket ligado na porta {self.client_socket.getsockname()[1]}')

    def packet_loss(self) -> bool:
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
        return b' '.join([str(ack_bit).encode(), str(self.expected_bit).encode(), data])

    def get_header(self, message: bytes) -> tuple:
        return message.split(b' ', 2)  # ack, bit, data

    def send_pkt(self, data: bytes, addr: tuple) -> None:
        sndpkt = self.make_pkt(0, data)

        if not self.packet_loss():
            self.client_socket.sendto(sndpkt, addr)
        else:
            print(f'Pacote {self.expected_bit} perdido (simulado).')

        self.rcv_ack(data)

    def send_ack(self, addr: tuple) -> None:
        sndpkt = self.make_pkt(1, b'')
        self.client_socket.sendto(sndpkt, addr)
        self.update_expected_bit()

    def listen(self):
        """Thread que escuta o socket e separa mensagens em filas apropriadas."""
        print("Thread de escuta iniciada...\n")
        while self.running:
            try:
                message, addr = self.client_socket.recvfrom(BUFFER_SIZE)
                rcv_ack, rcv_bit, rcv_data = self.get_header(message)
                if self.is_ack_bit(rcv_ack):
                    self.ack_queue.put((rcv_bit, addr))
                else:
                    self.data_queue.put((rcv_bit, rcv_data, addr))
                    self.rcv_packet()
            except socket.timeout:
                continue

    def rcv_packet(self) -> None:
        """Recebe pacotes e processa ACKs."""
        rcv_bit, rcv_data, addr = self.data_queue.get(timeout=1)
        self.send_ack(addr)
        self.last_packet_received = rcv_data
        print(f"[Servidor]: {rcv_data.decode()}")
            

    def rcv_ack(self, data: bytes) -> None:
        """Aguarda e processa ACKs da fila."""
        while True:
            try:
                rcv_bit, addr = self.ack_queue.get(timeout=1)

                if self.is_expected_bit(rcv_bit):
                    self.update_expected_bit()
                    return
                else:
                    self.send_pkt(data, addr)
                    return

            except queue.Empty:
                self.send_pkt(data, SERVER_ADDRESS)
                return

    def run(self):
        """Loop principal do cliente."""
        thread = threading.Thread(target=self.listen, daemon=True)
        thread.start()

        print("Digite mensagens para enviar ao servidor. Digite 'bye' para sair.")
        while self.running:
            message = input("> ")
            if message.lower() == "bye":
                self.send_pkt(message.encode(), SERVER_ADDRESS)
                print("Encerrando cliente...")
                self.running = False
                break
            self.send_pkt(message.encode(), SERVER_ADDRESS)

        self.client_socket.close()


if __name__ == '__main__':
    client = Client()
    client.run()
