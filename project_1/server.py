from socket import *

# Constants
HOST = "localhost"
SERVER_PORT = 3562
SERVER_ADDRESS = (HOST, SERVER_PORT)
BUFFER_SIZE = 1024
FILE_DIRECTORY = "files/"
ARCHIVED_PREFIX = "archived_"
DOWNLOADED_PREFIX = "downloaded_"


def get(file_name: str) -> bytes:
    with open(FILE_DIRECTORY + file_name, "rb") as local_file:
        return local_file.read()


def post(file_name: str, file_data: bytes) -> None:
    try:
        with open(FILE_DIRECTORY + ARCHIVED_PREFIX + file_name, "xb") as local_file:
            local_file.write(file_data)
    except FileExistsError:
        raise ValueError("File already exists.")


def receive_file(server_socket: socket, file_size: int) -> bytes:
    received_data = b""
    
    while len(received_data) < file_size:
        chunk, _ = server_socket.recvfrom(BUFFER_SIZE)
        received_data += chunk
        
    return received_data


def send_file(server_socket: socket, client_address: tuple, content: bytes) -> None:
    file_size = str(len(content))
    server_socket.sendto(file_size.encode(), client_address)

    for i in range(0, len(content), BUFFER_SIZE):
        chunk = content[i:i+BUFFER_SIZE]
        server_socket.sendto(chunk, client_address)


def handle_client_request(server_socket: socket) -> bool:
    header, client_address = server_socket.recvfrom(BUFFER_SIZE)
    header = header.decode()

    action, header = header.split(' ', 1)

    print(f"Command received from client: {action}.")

    if action == "post":
        file_name, file_size = header.split(' ')
        file_size = int(file_size)
        print(f"Receiving file {file_name} of size {file_size} bytes.")
        received_data = receive_file(server_socket, file_size)
        post(file_name, received_data)
    elif action == "get":
        file_name = header.strip()
        content = get(file_name)
        print(f"Sending file: {file_name}.")
        send_file(server_socket, client_address, content)
    elif action == "close":
        print("Closing connection.")
        return False

    print(f"Command accomplished.")
    return True


def main():
    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(SERVER_ADDRESS)

    print("The server is ready.")
    running = True
    while running:
        running = handle_client_request(server_socket)
    print("Server is shutting down.")    
    
    server_socket.close()
    print("Server socket closed.")

if __name__ == "__main__":
    main()