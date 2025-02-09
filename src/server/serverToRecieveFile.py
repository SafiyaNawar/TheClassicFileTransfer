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
def receive_file_from_client(connection):

    file_name = connection.recv(CHUNK_SIZE).decode() # Client initiates contact by sending filename

    # Check if the client sent an error message instead of the file name incase file does not exist
    if file_name.startswith("ERROR:"):
        print(file_name)  # Print the error message as it is
        connection.close()  # Close the connection
        return None  # Return None if there's an error

    print(f"Receiving file: {file_name}") # Proceed to receive file if name is correct

    connection.send(b"READY")  # Send acknowledgment that server is ready to receive the file content
    connection.settimeout(3)  # Prevent indefinite blocking

    try:
        # Creates a file and writes the content sent over by the client
        with open(file_name, "wb") as f:
            while True:
                try:
                    data = connection.recv(CHUNK_SIZE)
                    if not data:  # Connection closed
                        break
                    # Check if "END" is part of the data
                    if data.endswith(b"END"):
                        f.write(data[:-3])  # Write everything except "END"
                        break
                    f.write(data)  # Write normally if "END" is not present
                except socket.timeout:
                    break

        print("File received successfully. Chunking and sending back...")
        return file_name

    except Exception as ex:
        print(f"Error during file receiving process: {ex}")
        return None

def resend_file_to_client(connection, file_name):

    try:
        # Read the received file and split it into chunks for resending it back to the client
        with open(file_name, "rb") as f:
            file_data = f.read()
        checksum = calculate_the_checksum(file_data)
        connection.sendall(checksum.encode())  # Send checksum before data

        for chunk in split_file_into_chunks(file_name):
            connection.sendall(chunk)
        connection.sendall(b"END")  # Indicate end of transmission
        print("File transfer complete.")

    except FileNotFoundError:
        print(f"Error: File {file_name} not found.")

    except Exception as ex:
        print(f"Error while resending file: {ex}")


def main():
    try:

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((HOST, PORT))
        server_socket.listen(1)
        print(f"Server listening on {HOST}:{PORT}")

        while True:  # Keeps the server running for multiple clients
            try:
                connection, client_address = server_socket.accept()
                print(f"Connection initiated from {client_address}")

                file_name = receive_file_from_client(connection)
                if file_name:  # In the case where it does not exist
                    resend_file_to_client(connection, file_name)

                connection.close()  # Close connection after one client
                print("Connection closed.\nWaiting for next client...")
            except Exception as ex:
                print("Unable to connect to client")

    except Exception as e:
        print("Error during server setup, server down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
