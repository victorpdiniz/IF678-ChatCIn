from socket import *
from threading import Thread
from rdt import RDT

# Constants
SERVER_PORT = 1057
BUFFER_SIZE = 1024
SEQ_NUM_SIZE = 50
ACK_BIT_SIZE = 50
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
FILE_DIRECTORY = 'files/'
ARCHIVED_PREFIX = 'archived_'

class Server:
    def __init__(self):
        """Initialize the server socket and bind it."""
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        print('The server is ready to receive connections.')

    def open_file(self, file_name: str) -> bytes:
        """Retrieve file content from the local storage."""
        with open(FILE_DIRECTORY + file_name, 'rb') as local_file:
            return local_file.read()
    
    def save_file(self, file_name: str, file_data: bytes) -> None:
        """Save file content to the local storage."""
        with open(FILE_DIRECTORY + ARCHIVED_PREFIX + file_name, 'wb') as local_file:
            local_file.write(file_data)
    
    def receive_file(self, rdt: RDT, file_name: str, file_size: int) -> None:
        """Receive file content."""
        received_data = b''
        while len(received_data) < file_size:
            chunk = rdt.rcv_packet()
            received_data += chunk

        self.save_file(file_name, received_data)
        print(f'File {file_name} received and saved.')

    def send_file(self, rdt: RDT, client_address: tuple, content: bytes) -> None:
        """Send file data in chunks."""
        print(f'Sending file to {client_address}...')
        for i in range(0, len(content), BUFFER_SIZE - (SEQ_NUM_SIZE + ACK_BIT_SIZE)):
            chunk = content[i:i+(BUFFER_SIZE - (SEQ_NUM_SIZE + ACK_BIT_SIZE))]
            rdt.send_pkt(chunk, client_address)
        print('File transfer completed.')

    def handle_client_request(self, client_address: tuple):
        """Handle client requests in a separate thread."""
        rdt = RDT(self.server_socket)
        
        while True:
            header = rdt.rcv_packet()
            action, file_name, file_size = header.decode().split(' ', 2)
            file_size = None if file_size == 'None' else int(file_size)

            print(f'Command from {client_address}: {action} {file_name} ({file_size} bytes).')

            if action == 'post':
                self.receive_file(rdt, file_name, file_size)
            
            elif action == 'get':
                content = self.open_file(file_name)
                file_size = str(len(content)).encode()
                
                # Send file information
                rdt.send_pkt(file_size, client_address)

                # Send file data
                self.send_file(rdt, client_address, content)
            
            elif action == 'close':
                print(f'Client {client_address} disconnected.')
                break

    def run(self):
        """Listen for clients and delegate each to a new thread."""
        n_threads = 0
        while True:
            _, client_address = self.server_socket.recvfrom(BUFFER_SIZE)
            print(f'New client connected: {client_address}')
            client_thread = Thread(target=self.handle_client_request, name=str(n_threads) , args=(client_address))
            client_thread.start()
            n_threads += 1

if __name__ == "__main__":
    server = Server()
    server.run()
