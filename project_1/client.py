from socket import *

# Constants
HOST = "localhost"
SERVER_PORT = 3562
SERVER_ADDRESS = (HOST, SERVER_PORT)
BUFFER_SIZE = 1024
FILE_DIRECTORY = "files/"
DOWNLOADED_PREFIX = "downloaded_"


def get(file_name: str) -> bytes:
    with open(FILE_DIRECTORY + file_name, "rb") as local_file:
        return local_file.read()


def post(file_name: str, file_data: bytes) -> None:
    try:
        with open(FILE_DIRECTORY + DOWNLOADED_PREFIX + file_name, "xb") as local_file:
            local_file.write(file_data)
    except FileExistsError:
        raise ValueError("File already exists.")


def receive_file(client_socket: socket, file_name: str) -> bytes:
    message, _ = client_socket.recvfrom(BUFFER_SIZE)
    file_size = int(message.decode())
    
    print(f"File {file_name} is {file_size} bytes.")

    received_data = b''
    while len(received_data) < file_size:
        chunk, _ = client_socket.recvfrom(BUFFER_SIZE)
        received_data += chunk
        
    return received_data


def send_file(client_socket: socket, content: bytes) -> None:
    for i in range(0, len(content), BUFFER_SIZE):
        chunk = content[i:i+BUFFER_SIZE]
        client_socket.sendto(chunk, SERVER_ADDRESS)


def main():
    client_socket = socket(AF_INET, SOCK_DGRAM)
    print("The client is ready.")

    while True:
        action = input("Enter action: ").strip().lower()

        if action == "close":
            print("Closing the client socket.")
            client_socket.sendto("close".encode(), SERVER_ADDRESS)
            break

        if action == "post":
            file_name = input("Enter file name: ").strip()
            content = get(file_name)
            file_size = str(len(content))                
            
            message = f"{action} {file_name} {file_size}"
            client_socket.sendto(message.encode(), SERVER_ADDRESS)
            
            print(f"Sending file {file_name}.")
            send_file(client_socket, content)
        elif action == "get":
            file_name = input("Enter file name: ").strip()
            message = f"{action} {file_name}"
            client_socket.sendto(message.encode(), SERVER_ADDRESS)
            
            print(f"Receiving file {file_name}.")
            received_data = receive_file(client_socket, file_name)
            post(file_name, received_data)
        else:
            print("Invalid action. Use get, post, or close.")

    client_socket.close()
    print("Socket closed.")


if __name__ == "__main__":
    main()