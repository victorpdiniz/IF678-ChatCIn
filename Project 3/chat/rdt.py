import socket
import random

# Constants
BUFFER_SIZE = 1024
SERVER_PORT = 1057
CLIENT_PORT = 1058
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
CLIENT_ADDRESS = (HOST, CLIENT_PORT)

class RDT:
    def __init__(self, sockets: socket):
        """Initialize variables and timers."""
        self.socket = sockets
        self.sender_address = None
        self.expected_bit = 0
        self.timeout = 1
        self.socket.settimeout(self.timeout)
        self.last_packet_received = None
    
    def reset(self) -> None:
        """Reset the timer."""
        self.expected_bit = 0
        self.sender_address = None
        self.timeout = 1
        self.last_packet_received = None
        self.socket.settimeout(self.timeout)
    
    def packet_loss(self) -> bool:
        return random.random() < 0.3
    
    def is_duplicated(self, data: bytes) -> bool:
        return data == self.last_packet_received

    def is_expected_bit(self, bit: bytes) -> bool:
        """Check if the received bit is the expected bit."""
        return bit == str(self.expected_bit).encode()
    
    def is_ack_bit(self, bit: bytes) -> bool:
        """Check if the received packet is an ACK."""
        return bit == b'1'
        
    def update_expected_bit(self) -> None:
        """Update the alternating bit."""
        self.expected_bit = 1 - self.expected_bit

    def make_pkt(self, ack_bit: int, data: bytes) -> bytes:
        """Builds packet for sending."""
        data = b' '.join([str(ack_bit).encode(), str(self.expected_bit).encode(), data])
        return data
    
    def get_header(self, message: bytes) -> tuple:
        """Extract header information from message."""
        rcv_ack, rcv_bit, rcv_data =  message.split(b' ', 2)
        return rcv_ack, rcv_bit, rcv_data

    def send_pkt(self, data: bytes, receiver_address: tuple) -> None:
        """Send packet to receiver."""
        sndpkt = self.make_pkt(0, data)
        
        if not self.packet_loss():
            self.socket.sendto(sndpkt, receiver_address)

        self.rcv_ack(data)
    
    def send_ack(self, sender_address: tuple) -> None:
        """Send ACK to sender."""
        sndpkt = self.make_pkt(1, b'')
        
        if not self.packet_loss():
            self.socket.sendto(sndpkt, sender_address)
        
        self.update_expected_bit()
    
    def rcv_packet(self) -> tuple[bytes, tuple]:#alterei isso para tentar devolver o addr
        """Receive packet from sender."""
        try:
            message, sender_address = self.socket.recvfrom(BUFFER_SIZE)
            self.sender_address = sender_address
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            
            if self.is_ack_bit(rcv_ack):
                return self.rcv_packet()
            
            elif self.is_expected_bit(rcv_bit):
                self.send_ack(sender_address)
                self.last_packet_received = rcv_data
                return rcv_data,sender_address
            else:
                print(f'Received packet {rcv_bit} expected packet {self.expected_bit}.')
                return self.rcv_packet(),sender_address

        except socket.timeout:
            self.update_expected_bit()
            self.send_ack(CLIENT_ADDRESS)
            return self.rcv_packet()
        
    def rcv_ack(self, data: bytes) -> None:
        """Receive ACK from receiver."""
        try:
            message, sender_address = self.socket.recvfrom(BUFFER_SIZE)
            self.sender_address = sender_address
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            
            if not self.is_ack_bit(rcv_ack):
                if self.is_duplicated(rcv_data):
                    self.update_expected_bit()
                    self.send_ack(sender_address)
                    self.send_pkt(data, sender_address)
                else:
                    self.rcv_ack(data)
                return
            
            if self.is_expected_bit(rcv_bit):
                self.update_expected_bit()
            else:
                self.send_pkt(data, sender_address)
                
            return
            
        except socket.timeout:
            self.send_pkt(data, CLIENT_ADDRESS)
