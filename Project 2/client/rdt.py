import socket
import random

# constant
BUFFER_SIZE = 1024

class RDT:
    def __init__(self, sockets: socket):
        """Initialize variables and timers."""
        self.socket = sockets
        self.sender_address = None
        self.expected_bit = 0
        self.timeout = 1
        self.socket.settimeout(self.timeout)
        print('RDT initialized with expected bit 0.')
        print(f'Timeout set to {self.timeout} seconds.')
    
    def reset(self) -> None:
        """Reset the timer."""
        self.expected_bit = 0
        self.sender_address = None
        self.timeout = 5
        self.socket.settimeout(self.timeout)
        print('Timer and expected bit reset.')
    
    def packet_loss(self) -> bool:
        return random.random() < 0.3

    def is_expected_bit(self, bit: bytes) -> bool:
        """Check if the received bit is the expected bit."""
        return bit == str(self.expected_bit).encode()
    
    def is_ack_bit(self, bit: bytes) -> bool:
        """Check if the received packet is an ACK."""
        return bit == b'1'
        
    def update_expected_bit(self) -> None:
        """Update the alternating bit."""
        self.expected_bit = 1 - self.expected_bit
        print('Expected bit updated to:', self.expected_bit)

    def make_pkt(self, ack_bit: int, data: bytes) -> bytes:
        """Builds packet for sending."""
        data = b' '.join([str(ack_bit).encode(), str(self.expected_bit).encode(), data])
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
            if not self.packet_loss():
                print(f'Send: ACK {self.expected_bit} sent.')
                self.socket.sendto(sndpkt, receiver_address)
            else:
                print('Send: Packet lost.')
            self.update_expected_bit()
        # Send data
        else:
            if not self.packet_loss():
                print(f'Send: Packet {self.expected_bit} sent.')
                self.socket.sendto(sndpkt, receiver_address)
            else:
                print('Send: Packet lost.')
                
            # Receive ACK 
            self.receive(data, 1)

    def receive(self, data: bytes, ack_bit: int) -> bytes:
        """Receive data from sender."""
        # Receive packet
        try:
            message, self.sender_address = self.socket.recvfrom(BUFFER_SIZE)
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            
            # Received ACK
            if self.is_ack_bit(rcv_ack):
                # Received correct ACK
                if self.is_expected_bit(rcv_bit):
                    print(f'Receive: ACK {rcv_bit} received.')
                    self.update_expected_bit()
                # Received wrong ACK
                else:
                    print(f'Receive: ACK {rcv_bit} received. Expected ACK {self.expected_bit}.')
                    self.receive(data, ack_bit)
                
            else:
                if self.is_expected_bit(rcv_bit):
                # Send ACK
                    print(f'Receive: Packet {rcv_bit} received.')
                    self.send(b'', self.sender_address, 1)
                    return rcv_data
                
                # Send ACK for last known bit
                else:
                    print(f'Receive: Packet {rcv_bit} received. Expected packet {self.expected_bit}.')
                    self.update_expected_bit()
                    self.send(b'', self.sender_address, 1)
                    return self.receive(data, 0)
        # Timeout
        except socket.timeout:
            if ack_bit == 1:
                print(f'Timeout for ACK {self.expected_bit}.')
                self.send(data, self.sender_address, 0)
            else:
                print(f'Timeout for packet {self.expected_bit}.')
                self.update_expected_bit()
                self.send(b'', self.sender_address, 1)
                self.receive(data, 0)
