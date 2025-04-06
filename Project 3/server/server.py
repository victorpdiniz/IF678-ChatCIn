from socket import *
from rdt import RDT
from threading import Thread


# Constants
SERVER_PORT = 1057
BUFFER_SIZE = 1024
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
FILE_DIRECTORY = 'files/'
ARCHIVED_PREFIX = 'archived_'

class Server:
    def __init__(self):
        """Initialize the server socket and bind it."""
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        print('The server is ready.')
        
    def handle_client_request(self, server_rdt: RDT) -> bool:
        """Process incoming client requests."""
        rdt = server_rdt
        
        content, sender = rdt.rcv_pkt()

        print(f'Received message: {content}')
        
        # Broadcast the received message to all clients addresses except the sender in self.clients[addr]
        for addr in rdt.clients:
            if addr != sender:
                rdt.send_pkt(content, addr)


    def run(self):
        """Run the server loop to handle client requests."""
        running = True
        server_rdt = RDT(self.server_socket)
        while running:
            self.handle_client_request(server_rdt)
        
        self.server_socket.close()

if __name__ == "__main__":
    server = Server()
    server.run()