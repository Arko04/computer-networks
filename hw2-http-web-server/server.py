#import socket module
from socket import *
import sys # In order to terminate the program

serverSocket = socket(AF_INET, SOCK_STREAM)

#Prepare a sever socket
#Fill in start
serverPort = 6789 # Use port 6789 as in the example
serverSocket.bind(('', serverPort)) # Bind to all available interfaces on this port
serverSocket.listen(1) # Start listening, with a backlog of 1
#Fill in end

while True:
    #Establish the connection
    print('Ready to serve...')

    #Fill in start
    connectionSocket, addr = serverSocket.accept() # Accept an incoming connection
    #Fill in end                                                                

    try:
        #Fill in start
        message = connectionSocket.recv(1024).decode() # Receive the HTTP request (up to 1024 bytes)
        #Fill in end
        
        print(message)  # Print the received message for debugging

        filename = message.split()[1] # Parse the filename from the request (e.g., /HelloWorld.html)
        f = open(filename[1:]) # Open the file, stripping the leading '/'

        #Fill in start
        outputdata = f.read() # Read the entire content of the file
        #Fill in end

        #Send one HTTP header line into socket
        #Fill in start
        # Send the "200 OK" status line, followed by a blank line to end the headers
        connectionSocket.send('HTTP/1.1 200 OK\r\n\r\n'.encode())
        #Fill in end

        #Send the content of the requested file to the client
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        
        connectionSocket.close() 

    except IOError:
        #Send response message for file not found
        #Fill in start
        response = 'HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>'
        connectionSocket.send(response.encode())
        #Fill in end

        #Close client socket
        #Fill in start
        connectionSocket.close() 
        #Fill in end

serverSocket.close()
sys.exit() #Terminate the program after sending the corresponding data