import socket
import hashlib

from src.constants import CHUNK_SIZE, HOST,PORT


# Calculates the checksum for the data using the hashlib package
def calculate_the_checksum(data):
    return hashlib.md5(data).hexdigest()


# Client starts to send the file over the established connection to the server
def start_the_client(file_path, host=HOST, port=PORT):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    file_name = file_path.split('/')[-1]
    client_socket.send(file_name.encode())  # Send filename first

    acknowledgment_from_server = client_socket.recv(CHUNK_SIZE).decode()  # Wait for server acknowledgment
    if acknowledgment_from_server != "READY":
        print("Server did not acknowledge. Exiting.")
        client_socket.close()
        return

    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            client_socket.sendall(chunk)

    client_socket.sendall(b"END")  # Indicate end of transmission of file
    print("File has been uploaded. Waiting for response...")

    # Receive checksum from server
    received_checksum = client_socket.recv(32).decode()
    print(f"Expected checksum: {received_checksum}")

    # Receive the file chunks from the server
    received_data = b""
    while True:
        chunk = client_socket.recv(CHUNK_SIZE)
        if chunk == b"END" or chunk == b"":
            break
        received_data += chunk

    # Remove the "END" marker from the received data
    received_data = received_data.replace(b"END", b"")

    #Compute checksum on the resent data/file
    computed_checksum = calculate_the_checksum(received_data)
    print(f"Received checksum: {computed_checksum}")

    if received_checksum == computed_checksum:
        with open("received_" + file_name, "wb") as f:
            f.write(received_data)
        print("File reassembled and checksum matches. Transfer Successful!")
    else:
        print("Checksum mismatch!")

    client_socket.close()


if __name__ == "__main__":
    start_the_client("data.txt")
