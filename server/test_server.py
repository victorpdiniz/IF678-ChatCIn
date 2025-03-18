import socket
import time
import random

BUFFER_SIZE = 1024

# Generate random packet loss algorithm around 10% of the time
def packet_loss():
    return random.random() < 0.2
def udp_server(host='localhost', port=12345, timeout=3):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    rdt = RDT(server_socket)
    
    a = 0
    while a < 20:
        print('-' * 60)
        rdt.receive(b'', 0)
        time.sleep(1.5)
        a += 1

    server_socket.close()

class RDT:
    def __init__(self, sockets: socket):
        """Initialize variables and timers."""
        self.socket = sockets
        self.sender_address = None
        self.expected_bit = 0
        self.timeout = 5
        self.socket.settimeout(self.timeout)
        print('RDT initialized with expected bit 0.')
        print(f'Timeout set to {self.timeout} seconds.')
    
    def packet_loss(self) -> bool:
        return random.random() < 0.2

    def is_expected_bit(self, bit: bytes) -> bool:
        """Check if the received bit is the expected bit."""
        return bit == str(self.expected_bit).encode()
    
    def is_ack_bit(self, bit: bytes) -> bool:
        """Check if the received packet is an ACK."""
        return bit == b'1'
        
    def reset(self) -> None:
        """Reset the timer."""
        self.expected_bit = 0
        self.sender_address = None
        self.timeout = 5
        self.socket.settimeout(self.timeout)
        print('Timer and expected bit reset.')
    
    def update_expected_bit(self) -> None:
        """Update the alternating bit."""
        self.expected_bit = 1 - self.expected_bit
        # print(f'Alternating bit updated to {self.expected_bit}.')

    def make_pkt(self, ack_bit: int, data: bytes) -> bytes:
        """Builds packet for sending."""
        data = b' '.join([str(ack_bit).encode(), str(self.expected_bit).encode(), data])
        
        # if ack_bit:
        #     print(f'Packet ACK {self.expected_bit} builded.')
        # else:
        #     print(f'Packet {self.expected_bit} builded.')
            
        return data
    
    def get_header(self, message: bytes) -> tuple:
        """Extract header information from message."""
        rcv_ack, rcv_bit, rcv_data =  message.split(b' ', 2)
        return rcv_ack, rcv_bit, rcv_data
    
    def send(self, data: bytes, receiver_address: tuple, ack_bit: int) -> None:
        """Send data to receiver."""
        sndpkt = self.make_pkt(ack_bit, data)
        
        # Send ACK
        if ack_bit == 1:
            # print(f'Send: Sending ACK {self.expected_bit}.')
            if not self.packet_loss():
                self.socket.sendto(sndpkt, receiver_address)
            # else:
                # print('Send: Packet lost.')
            self.update_expected_bit()
        # Send data
        else:
            # print(f'Send: Sending packet {self.expected_bit}.')
            if not self.packet_loss():
                self.socket.sendto(sndpkt, receiver_address)
            # else:
            #     print('Send: Packet lost.')

            # Receive ACK 
            self.receive(data, 1)

    def receive(self, data: bytes, ack_bit: int) -> bytes:
        """Receive data from sender."""
        # Receive packet
        try:
            message, self.sender_address = self.socket.recvfrom(BUFFER_SIZE)
            # print(f'Receive: Packet received: {message}')
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            
            # Received ACK
            if self.is_ack_bit(rcv_ack):
                # print(f'Receive: Waiting for ACK {self.expected_bit}.')
                if self.is_expected_bit(rcv_bit):
                    # print(f'Receive: Received ACK {rcv_bit}.')
                    self.update_expected_bit()
                # Received wrong ACK
                else:
                    # print(f'Receive: Received ACK {rcv_bit}. Expected {self.expected_bit}. Resending.')
                    self.send(data, self.sender_address, 0)
            
            else:
                # print(f'Receive: Waiting for packet {self.expected_bit}.')
                # Send ACK
                if self.is_expected_bit(rcv_bit):
                    # print(f'Receive: Received packet {rcv_bit}. Sending ACK.')
                    self.send(b'', self.sender_address, 1)
                    return rcv_data
                
                # Send ACK for last known bit
                else:
                    # print(f'Receive: Received packet {rcv_bit}. Expected {self.expected_bit}. Sending ACK {1 - self.expected_bit}.')
                    self.update_expected_bit()
                    self.send(b'', self.sender_address, 1)
                    self.receive(data, 0)
        # Timeout
        except socket.timeout:
            if ack_bit == 1:
                # print(f'Receive: Timeout for ACK {self.expected_bit}. Resending.')
                self.send(data, self.sender_address, 0)
            else:
                # print(f'Receive: Timeout for packet {self.expected_bit}. Resending.')
                self.update_expected_bit()
                self.send(b'', self.sender_address, 1)
                self.receive(data, 0)


if __name__ == "__main__":
    udp_server()