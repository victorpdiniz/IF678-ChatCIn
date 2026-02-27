import socket
import time
import random

# Constants
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
        rdt.rcv_packet()
        a += 1

    server_socket.close()

class RDT:
    def __init__(self, sockets: socket):
        """Initialize variables and timers."""
        self.socket = sockets
        self.sender_address = None
        self.expected_bit = 0
        self.timeout = 1
        self.socket.settimeout(self.timeout)
        self.last_packet_received = None
        print('RDT initialized with expected bit 0.')
        print(f'Timeout set to {self.timeout} seconds.')
    
    def reset(self) -> None:
        """Reset the timer."""
        self.expected_bit = 0
        self.sender_address = None
        self.timeout = 5
        self.last_packet_received = None
        self.socket.settimeout(self.timeout)
        print('Timer and expected bit reset.')
    
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
        print('Expected bit updated to:', self.expected_bit)

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
        
        # Send data
        if not self.packet_loss():
            print(f'Packet {self.expected_bit} sent.')
            self.socket.sendto(sndpkt, receiver_address)
        else:
            print(f'Packet {self.expected_bit} lost.')

        # Receive ACK
        self.rcv_ack(data)
    
    def send_ack(self, sender_address: tuple) -> None:
        """Send ACK to sender."""
        sndpkt = self.make_pkt(1, b'')
        
        if not self.packet_loss():
            self.socket.sendto(sndpkt, sender_address)
            print(f'ACK {self.expected_bit} sent.')
        else:
            print(f'ACK {self.expected_bit} lost.')
        
        self.update_expected_bit()
    
    def rcv_packet(self) -> bytes:
        """Receive packet from sender."""
        try:
            message, sender_address = self.socket.recvfrom(BUFFER_SIZE)
            print(message)
            self.sender_address = sender_address
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            
            # Received ACK expected packet
            if self.is_ack_bit(rcv_ack):
                print(f'Received ACK {rcv_bit} expected packet {self.expected_bit}.')
                return self.rcv_packet()
            
            # Correct packet
            elif self.is_expected_bit(rcv_bit):
                print(f'Received packet {rcv_bit}.')
                self.send_ack(sender_address)
                self.last_packet_received = rcv_data
                return rcv_data
            
            # Received wrong packet
            else:
                print(f'Received packet {rcv_bit} expected packet {self.expected_bit}.')
                self.rcv_packet()
                return
                

        except socket.timeout:
            print(f'Timeout for packet {self.expected_bit}.')
            self.update_expected_bit()
            self.send_ack(self.sender_address)
            return self.rcv_packet()
        
    def rcv_ack(self, data: bytes) -> None:
        """Receive ACK from receiver."""
        try:
            message, sender_address = self.socket.recvfrom(BUFFER_SIZE)
            rcv_ack, rcv_bit, rcv_data = self.get_header(message)
            
            # Received packet expected ACK
            if not self.is_ack_bit(rcv_ack):
                
                # Packet received was already received?
                if self.is_duplicated(rcv_data):
                    # Then ACK this packet and send the actual packet
                    print(f'Received packet {rcv_bit} duplicated.')
                    self.update_expected_bit()
                    self.send_ack(sender_address)
                    self.send_pkt(data, sender_address)
                
                # Packet received was not already received
                else:
                    # Then don't ACK this packet, but wait for ACK from the last packet you sent
                    print(f'Received packet {rcv_bit}. Expected ACK {self.expected_bit}.')
                    self.rcv_ack(data)
                    
                return
            
            # Received correct ACK
            if self.is_expected_bit(rcv_bit):
                print(f'Received ACK {rcv_bit}.')
                self.update_expected_bit()
            
            # Received wrong ACK
            else:
                print(f'Received ACK {rcv_bit} expected ACK {self.expected_bit}.')
                self.send_pkt(data, sender_address)
                
            return
            
        except socket.timeout:
            print(f'Timeout for ACK {self.expected_bit}.')
            self.send_pkt(data, self.sender_address)

if __name__ == "__main__":
    udp_server()