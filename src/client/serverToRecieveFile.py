import socket
import hashlib
import os

from src.constants import CHUNK_SIZE, HOST, PORT

# Calculates the checksum for the data using the hashlib package
def calculate_the_checksum(data):
    return hashlib.md5(data).hexdigest()

#The data will be split into smaller chunks of size 1024
def split_file_into_chunks(file_path, chunk_size=CHUNK_SIZE):
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            yield chunk

#Server will start listening for client requests
def start_the_server(host=HOST, port=PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"Server listening on {host}:{port}")

    connection, client_address = server_socket.accept()
    print(f"Connection initiated from {client_address}")


    file_name = connection.recv(CHUNK_SIZE).decode() # Client initiates contact by sending filename
    print(f"Receiving file: {file_name}")

    connection.send(b"READY")  # Send acknowledgment that server is ready to receive the file content

    connection.settimeout(3)  # Prevent indefinite blocking

    # Creates a file and writes the content sent over by the client
    with open(file_name, "wb") as f:
        while True:
            try:
                data = connection.recv(CHUNK_SIZE)
                if not data or data == b"END":
                    break
                f.write(data)
            except socket.timeout:
                break

    # Now remove the "END" marker if it's present at the end of the file
    with open(file_name, "r+b") as f:
        f.seek(-3, 2)
        last_bytes = f.read(3)
        if last_bytes == b"END":
            f.truncate(f.tell() - 3)
    print("File received successfully. Chunking and sending back...")

    # Read the received file and split it into chunks for resending it back to the client
    with open(file_name, "rb") as f:
        file_data = f.read()
    checksum = calculate_the_checksum(file_data)

    connection.sendall(checksum.encode())  # Send checksum before data

    for chunk in split_file_into_chunks(file_name):
        connection.sendall(chunk)
    connection.sendall(b"END")  # Indicate end of transmission
    print("File transfer complete.")


if __name__ == "__main__":
    start_the_server()
