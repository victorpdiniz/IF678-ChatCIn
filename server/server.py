from socket import *

# Constants
SERVER_PORT = 1057
BUFFER_SIZE = 1024
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
FILE_DIRECTORY = 'files/'
ARCHIVED_PREFIX = 'archived_'


def get(file_name: str) -> bytes:
    """Retrieve file content from the server."""
    with open(FILE_DIRECTORY + file_name, 'rb') as local_file:
        return local_file.read()


def post(file_name: str, file_data: bytes) -> None:
    """Save file content to the server."""
    try:
        with open(FILE_DIRECTORY + ARCHIVED_PREFIX + file_name, 'xb') as local_file:
            local_file.write(file_data)
    except FileExistsError:
        raise ValueError("File already exists.")


def handle_client_request(server_socket):
    """Process incoming client requests."""
    header, client_address = server_socket.recvfrom(BUFFER_SIZE)
    header = header.decode()

    action, file_name, file_size = header.split(" ", 2)
    file_size = None if file_size == 'None' else int(file_size)

    print(f'Command received from client: {action} {file_name} ({file_size} bytes).')

    if action == 'post':
        received_data = receive_file(server_socket, file_size)
        post(file_name, received_data)
    elif action == 'get':
        send_file(server_socket, client_address, file_name)
    elif action == 'close':
        return False

    print(f'Command accomplished, response sent to: {client_address}.')
    return True


def receive_file(server_socket, file_size):
    """Receive file data in chunks."""
    received_data = b""
    while len(received_data) < file_size:
        chunk, _ = server_socket.recvfrom(BUFFER_SIZE)
        received_data += chunk
    return received_data


def send_file(server_socket, client_address, file_name):
    """Send file data to the client in chunks."""
    content = get(file_name)
    file_size = str(len(content))

    server_socket.sendto(file_size.encode(), client_address)

    for i in range(0, len(content), BUFFER_SIZE):
        chunk = content[i:i+BUFFER_SIZE]
        server_socket.sendto(chunk, client_address)


def main():
    """Initialize and run the server."""
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(SERVER_ADDRESS)

    print('The server is ready.')
    running = True
    
    while running:
        running = handle_client_request(server_socket)
    
    server_socket.close()


if __name__ == "__main__":
    main()
