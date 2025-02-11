from socket import *

# Constants
SERVER_PORT = 1057
CLIENT_PORT = 1058
BUFFER_SIZE = 1024
HOST = 'localhost'
SERVER_ADDRESS = (HOST, SERVER_PORT)
CLIENT_ADDRESS = (HOST, CLIENT_PORT)
FILE_DIRECTORY = 'files/'
DOWNLOADED_PREFIX = 'downloaded_'


def get(file_name: str) -> bytes:
    """Retrieve file content from the local storage."""
    with open(FILE_DIRECTORY + file_name, 'rb') as local_file:
        return local_file.read()


def post(file_name: str, file_data: bytes) -> None:
    """Save file content to the local storage."""
    try:
        with open(FILE_DIRECTORY + DOWNLOADED_PREFIX + file_name, 'xb') as local_file:
            local_file.write(file_data)
    except FileExistsError:
        raise ValueError("File already exists.")


def send_file(client_socket, action, file_name):
    """Send a file to the server."""
    content = get(file_name)
    file_size = str(len(content))
    message = f'{action} {file_name} {file_size}'
    client_socket.sendto(message.encode(), SERVER_ADDRESS)
    
    for i in range(0, len(content), BUFFER_SIZE):
        chunk = content[i:i+BUFFER_SIZE]
        client_socket.sendto(chunk, SERVER_ADDRESS)


def receive_file(client_socket, file_name):
    """Receive a file from the server."""
    message, _ = client_socket.recvfrom(BUFFER_SIZE)
    file_size = int(message.decode())
    print(f'File "{file_name}" is {file_size} bytes.')

    received_data = b""
    while len(received_data) < file_size:
        chunk, _ = client_socket.recvfrom(BUFFER_SIZE)
        received_data += chunk

    if received_data:
        post(file_name, received_data)
        response_message, _ = client_socket.recvfrom(BUFFER_SIZE)
        print(f'File "{file_name}" downloaded successfully.')


def main():
    """Initialize and run the client."""
    client_socket = socket(AF_INET, SOCK_DGRAM)
    client_socket.bind(CLIENT_ADDRESS)
    print('The client is ready.')

    while True:
        action = input('Enter action (get/post/close): ').strip().lower()

        if action == 'close':
            client_socket.sendto('close'.encode(), SERVER_ADDRESS)
            break

        file_name = input('Enter file name (with extension): ').strip()

        if action == 'post':
            send_file(client_socket, action, file_name)
        elif action == 'get':
            message = f'{action} {file_name} None'
            client_socket.sendto(message.encode(), SERVER_ADDRESS)
            receive_file(client_socket, file_name)
        else:
            print('Invalid action. Use "get", "post", or "close".')

    client_socket.close()


if __name__ == "__main__":
    main()