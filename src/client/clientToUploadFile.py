import os
import socket
import hashlib
import time

from src.constants import CHUNK_SIZE, HOST, PORT, RETRIES

# Calculates the checksum for the data using the hashlib package
def calculate_checksum(data):
    return hashlib.md5(data).hexdigest()


# Client starts to send the file over the established connection to the server
# Client sends chunks with the sequence number
def send_file_to_server(client_socket, file_path):
    file_name = os.path.basename(file_path)

    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        client_socket.send(b"ERROR: File does not exist.")
        client_socket.close()
        exit()

    client_socket.send(file_name.encode())
    server_acknowledgement = client_socket.recv(CHUNK_SIZE).decode()

    if server_acknowledgement != "READY":
        print("Server did not acknowledge. Exiting...")
        client_socket.close()
        exit()

    seq_num = 0
    with open(file_path, "rb") as f:
        while chunk := f.read(CHUNK_SIZE - len(str(seq_num)) - 1):  # Reserve space for sequence number
            # Prepare chunk with sequence number
            chunk_with_seq = f"{seq_num}:".encode() + chunk
            client_socket.sendall(chunk_with_seq)
            seq_num += 1

    # Send "END" marker
    client_socket.sendall(b"END")
    print("File sent successfully.")
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
    computed_checksum = calculate_checksum(received_data)
    print(f"Received checksum: {computed_checksum}")

    if received_checksum == computed_checksum:
        with open("received_" + file_name, "wb") as f:
            f.write(received_data)
        print("File reassembled and checksum matches. Integrity verified!")
    else:
        print("Checksum mismatch!")


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    # Take the file name as an input from the user
    file_path = input("Enter the file path to send: ").strip()

    file_name = send_file_to_server(client_socket, file_path)

    for attemp_number in range(RETRIES):
        try:
            receive_file(client_socket, file_name)
            break
        except Exception as e:
            print(f"Error: {e}. Retrying... ({attemp_number + 1}/{RETRIES})")
            time.sleep(2)
    else:
        print("Failed to receive file after multiple attempts.")


    client_socket.close()

if __name__ == "__main__":
    main()
