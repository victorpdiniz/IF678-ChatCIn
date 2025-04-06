from socket import *
from rdt import RDT
from threading import Thread

# Constants
SERVER_PORT = 1057
BUFFER_SIZE = 1024
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)

class Client:
    def __init__(self):
        """Initialize the client socket and bind it."""
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        print('The client is ready.')

    def run(self):
        """Run the client loop to send and receive files."""
        rdt = RDT(self.client_socket)
        
        thread = Thread(target=rdt.listen)
        thread.start()

        while True:
            message = input()

            rdt.send_pkt(message.encode(), SERVER_ADDRESS)

        
if __name__ == '__main__':
    client = Client()
    client.run()
