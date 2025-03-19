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
DOWNLOADED_PREFIX = 'downloaded_'


class Client:
    def __init__(self):
        """Initialize the client socket and bind it."""
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.bind(CLIENT_ADDRESS)
        print('The client is ready.')

    def open_file(self, file_name: str) -> bytes:
        """Retrieve file content from the local storage."""
        with open(FILE_DIRECTORY + file_name, 'rb') as local_file:
            return local_file.read()

    def save_file(self, file_name: str, file_data: bytes) -> None:
        """Save file content to the local storage."""
        with open(FILE_DIRECTORY + DOWNLOADED_PREFIX + file_name, 'wb') as local_file:
            local_file.write(file_data)

    def run(self):
        """Run the client loop to send and receive files."""
        rdt = RDT(self.client_socket)
        
        while True:
            action = input('Enter action (get/post/close): ').strip().lower()

            if action == 'close':
                rdt.send('close', SERVER_ADDRESS, 0)
                break

            file_name = input('Enter file name (with extension): ').strip()

            # Post file to the server
            if action == 'post':
                content = self.open_file(file_name)
                file_size = str(len(content))
                message = f'{action} {file_name} {file_size}'
                # Send file information
                print(message)
                rdt.send(message.encode(), SERVER_ADDRESS, 0)
                # Send file data
                for i in range(0, len(content), BUFFER_SIZE - (SEQ_NUM_SIZE + ACK_BIT_SIZE)):
                    chunk = content[i:i+(BUFFER_SIZE - (SEQ_NUM_SIZE + ACK_BIT_SIZE))]
                    rdt.send(chunk, CLIENT_ADDRESS, 0)
                
                # Receive response
                message = rdt.receive(b'', 0)
                if message == 'True'.encode():
                    print(f'File "{file_name}" uploaded successfully.')
                else:
                    print(f'File "{file_name}" could not be uploaded.')
                
            
            elif action == 'get':
                message = f'{action} {file_name} None'
                
                # Send file information
                print(f'Sent message: {message}')
                rdt.send(message.encode(), SERVER_ADDRESS, 0)
                
                # Receive file size
                message = rdt.receive(b'', 0).decode()
                print(f'Received message: {message}')
                file_size = int(message)
                print(f'File "{file_name}" is {file_size} bytes.')
                
                # Receive file data
                print('Receiving file data...')
                received_data = b''
                while len(received_data) < file_size:
                    print(len(received_data))
                    chunk = rdt.receive(b'', 0)
                    received_data += chunk
                    
                print('File data received. Waiting for confirmation message...')
                
                # Receive confirmation message
                # validation_message = rdt.receive(b'', 0).decode()
                # print(validation_message)
                # if validation_message == 'True':
                #     print(f'File "{file_name}" downloaded successfully.')
                # else:
                #     print(f'File "{file_name}" could not be downloaded.')
                
                # Save file
                self.save_file(file_name, received_data)
                
            else:
                print('Invalid action. Use "get", "post", or "close".')

        self.client_socket.close()
        
if __name__ == '__main__':
    client = Client()
    client.run()
