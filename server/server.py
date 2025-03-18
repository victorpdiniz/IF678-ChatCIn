from socket import *
from rdt import RDT

# Constants
SERVER_PORT = 1057
CLIENT_PORT = 1058
BUFFER_SIZE = 1024
SEQ_NUM_SIZE = 50
ACK_BIT_SIZE = 50
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
CLIENT_ADDRESS = (HOST, CLIENT_PORT)
FILE_DIRECTORY = 'files/'
ARCHIVED_PREFIX = 'archived_'

class Server:
    def __init__(self):
        """Initialize the server socket and bind it."""
        self.server_socket = socket(AF_INET, SOCK_DGRAM)
        self.server_socket.bind(SERVER_ADDRESS)
        print('The server is ready.')

    def open_file(self, file_name: str) -> bytes:
        """Retrieve file content from the local storage."""
        with open(FILE_DIRECTORY + file_name, 'rb') as local_file:
            return local_file.read()
    
    def save_file(self, file_name: str, file_data: bytes) -> None:
        """Save file content to the local storage."""
        with open(FILE_DIRECTORY + ARCHIVED_PREFIX + file_name, 'wb') as local_file:
            local_file.write(file_data)

    def handle_client_request(self, reliable_data_transfer: RDT) -> bool:
        """Process incoming client requests."""
        rdt = reliable_data_transfer
        header = rdt.receive(b'', 0)
        action, file_name, file_size = header.decode().split(' ', 2)
        file_size = None if file_size == 'None' else int(file_size)

        print(f'Command received from client: {action} {file_name} ({file_size} bytes).')
        if action == 'post':
            # Receive file data
            received_data = b''
            while len(received_data) < file_size:
                chunk = rdt.receive(b'', 0)
                received_data += chunk

            if received_data:
                self.save_file(file_name, received_data)
                message = rdt.receive(b'', 0)
                if message == 'True'.encode():
                    print(f'File "{file_name}" uploaded successfully.')
                else:
                    print(f'File "{file_name}" could not be uploaded.')
            
            self.save_file(file_name, received_data)
            
        elif action == 'get':
            content = self.open_file(file_name)
            file_size = str(len(content))
            message = f'{file_size}'
            
            # Send file information
            rdt.send(message.encode(), CLIENT_ADDRESS, 0)
            
            # Send file data
            print('Sending file data...')
            for i in range(0, len(content), BUFFER_SIZE - (SEQ_NUM_SIZE + ACK_BIT_SIZE)):
                chunk = content[i:i+(BUFFER_SIZE - (SEQ_NUM_SIZE + ACK_BIT_SIZE))]
                rdt.send(chunk, CLIENT_ADDRESS, 0)
            print('File data sent. Sending confirmation message...')
            
            # Send confirmation message
            message = 'True'.encode()
            rdt.send(message, CLIENT_ADDRESS, 0)
            print(f'File "{file_name}" uploaded successfully.')
            
        elif action == 'close':
            return False

        print(f'Command accomplished, response sent to: {CLIENT_ADDRESS}.')
        rdt.send('True'.encode(), CLIENT_ADDRESS, 0)
        return True

    def run(self):
        """Run the server loop to handle client requests."""
        running = True
        rdt = RDT(self.server_socket)
        while running:
            running = self.handle_client_request(rdt)
        
        self.server_socket.close()

if __name__ == "__main__":
    server = Server()
    server.run()