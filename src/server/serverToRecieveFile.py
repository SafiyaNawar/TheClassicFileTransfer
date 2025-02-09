import socket
import hashlib
import os

from src.constants import CHUNK_SIZE, HOST, PORT

#Data is being chunked down to small size of 1024 bytes
def split_data_into_chunks(file_path, chunk_size=CHUNK_SIZE):
    with open(file_path, "rb") as file_on_server:
        while chunk := file_on_server.read(chunk_size):
            yield chunk


# Calculates the checksum for the data using the hashlib package
def calculate_the_checksum(data):
    return hashlib.md5(data).hexdigest()


#Server will start listening for client requests
def receive_file_from_client(connection):

    file_name = connection.recv(CHUNK_SIZE).decode() # Client initiates contact by sending filename

    # Check if the client sent an error message instead of the file name incase file does not exist
    if file_name.startswith("ERROR:"):
        print(file_name)  # Print the error message as it is
        connection.close()  # Close the connection
        return None  # Return None if there's an error

    print(f"Receiving file: {file_name}") # Proceed to receive file if name is correct
    connection.send(b"READY")

    sequence_number = 0
    with open(file_name, "wb") as server_file:
        while True:
            try:
                data = connection.recv(CHUNK_SIZE)
                if not data:
                    break

                # Check for "END" marker and do not append this to file
                chunk_end = False
                if data.endswith(b"END"):
                    chunk_data = data[:-3]  # Remove "END"
                    chunk_end = True
                else:
                    chunk_data = data

                # Split sequence number from the actual chunk data
                try:
                    sequence_marker, chunk_data = chunk_data.split(b":", 1)
                    received_sequence_number = int(sequence_marker.decode())

                    if received_sequence_number != sequence_number:
                        print(f"Out-of-order chunk received. Expected {sequence_number}, but got {received_sequence_number}.")
                    else:
                        sequence_number += 1

                    server_file.write(chunk_data)  # Write actual chunk data excluding the sequence number to file

                    if chunk_end:
                        break

                except ValueError:
                    print("Error: Invalid chunk format or corrupted data received.")
                    break  # Exit if there's an error in chunk format

            except socket.timeout:
                break  # Exit if a timeout occurs

    print("File received successfully.")
    return file_name


def resend_file_to_client(connection, file_name):

    try:
        # Read the received file and split it into chunks for resending it back to the client
        with open(file_name, "rb") as saved_server_file:
            file_data = saved_server_file.read()
        checksum = calculate_the_checksum(file_data)
        connection.sendall(checksum.encode())  # Send checksum before data

        for chunk in split_data_into_chunks(file_name):
            connection.sendall(chunk)
        connection.sendall(b"END")  # Indicate end of data transmission
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

        # Server is up and running for client requests one after another
        while True:
            try:
                connection, client_address = server_socket.accept()
                print(f"Connection initiated from {client_address}")

                file_name = receive_file_from_client(connection)
                print("File received successfully. Chunking and sending back...")
                if file_name:  # In the case where it does not exist, do not resend file
                    resend_file_to_client(connection, file_name)

                connection.close()  # Close connection after each client
                print("Connection closed for this client.\nWaiting for the next client...")
            except Exception as ex:
                print("Unable to connect to client.")

    except Exception as e:
        print("Error during server setup, server down.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
