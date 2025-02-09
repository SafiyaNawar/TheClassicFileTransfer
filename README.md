# TheClassicFileTransfer

This model simulates the client-server architecture for simple file transfer.
The server is up and actively listening for client requests on port 12345, ready for file uploads.
Clients can upload files one after another, interacting in succession.
This allows the client to upload a file by taking file name as input, they are prompted to provide the file path. 
The server will process this file transfer request, ensuring a smooth exchange of data between the client and server.


CLIENT

A client will the initiate contact to the server by sending the file name followed by file data as chunks.
It will chunk the data and append a sequence number to it, ensuring order of the chunks to be reconstructed by the server.
Once it sends the entire file, it waits to receive the file back from the server. 
Once received, it checks the integrity of the data sent by calculating and comparing the checksum on the data.


SERVER

The server receives a connection request by getting a file_path. It will extract the file name.
The data is received as chunks with a sequence number from the client, it will extract the chunk_data and append it to the file.
It then calculates the checksum, sends to the client. Then proceeds to transmit the file in form of chunks back to the client.
The client reassembles the file in the correct order and verifies its integrity using a checksum.
It then closes the connection for that client and waits for requests from other clients.    