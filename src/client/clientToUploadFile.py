import os
import socket
import hashlib

from src.constants import CHUNK_SIZE, HOST,PORT

# Calculates the checksum for the data using the hashlib package
def calculate_the_checksum(data):
    return hashlib.md5(data).hexdigest()


# Client starts to send the file over the established connection to the server
def send_file_to_server(client_socket, file_path):
    file_name = os.path.basename(file_path)

    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        client_socket.send(b"ERROR: File does not exist.")  # Send error message to server
        client_socket.close()
        exit()

    # Send the file name to indicate file transfer to the server, catch any exceptions
    client_socket.send(file_name.encode())

    try:
        server_acknowledgement = client_socket.recv(CHUNK_SIZE).decode()  # Wait for server acknowledgment
        if server_acknowledgement != "READY":
            print("Server did not acknowledge. Exiting...")
            client_socket.close()
            exit()
    except socket.timeout:
        print("Server acknowledgment timed out. Exiting...")
        client_socket.close()
        exit()
    except socket.error as e:
        print(f"Error receiving server acknowledgment: {e}")
        client_socket.close()
        exit()

    # Open the file and send chunks with sequence numbers
    with open(file_path, "rb") as f:
        seq_num = 0
        while chunk := f.read(CHUNK_SIZE):
            # Prefix the chunk with the sequence number
            tagged_chunk = f"{seq_num}:{chunk.decode(errors='ignore')}".encode()  # Tag the chunk with seq_num
            client_socket.sendall(tagged_chunk)
            seq_num += 1
            print(tagged_chunk)

    client_socket.sendall(b"END")  # Indicate end of transmission
    print("File has been uploaded. Waiting for response...")

    return file_name


# Client starts to send the file over the established connection to the server
def receive_file(client_socket, file_name):

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

    # Compute checksum on the resent data/file
    computed_checksum = calculate_the_checksum(received_data)
    print(f"Received checksum: {computed_checksum}")

    if received_checksum == computed_checksum:
        with open("received_" + file_name, "wb") as f:
            f.write(received_data)
        print("File reassembled and checksum matches. Transfer Successful!")
    else:
        print("Checksum mismatch!")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Take the file name as an input from the user
    file_path = input("Enter the file path to send: ").strip()

    file_name = send_file_to_server(client_socket, file_path)
    receive_file(client_socket, file_name)

    client_socket.close()

if __name__ == "__main__":
    main()
