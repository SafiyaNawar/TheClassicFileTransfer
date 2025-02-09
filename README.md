# TheClassicFileTransfer
Simulates a client-server architecture for file transfer. Server is up and running on port 12345.
Clients can upload data one after another to the server.
Allows the client to upload a file to the server. The file path to be uploaded is taken as an input.


CLIENT

A client will the initiate contact to the server by sending the file name followed by file data as chunks.
It also waits to receive the file back from the client and checks the integrity by calculating the checksum.


SERVER

The server splits the file into smaller chunks, and saves it in a fiel.
It then assigns each chunk a sequence number, and transmits these chunks back to the client.
The client reassembles the file in the correct order and verifies its integrity using a checksum.
