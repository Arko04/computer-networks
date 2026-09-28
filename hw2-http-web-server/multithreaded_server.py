#import socket module
from socket import *
import sys # In order to terminate the program
import threading # Import the threading module

def handle_client(connectionSocket, addr):
    """
    This function handles the entire request/response cycle for a single client
    in its own thread.
    """
    print(f"[Thread for {addr}] Connection started.")
    try:
        # Receive the HTTP request from this client
        message = connectionSocket.recv(1024).decode()
        
        # Ensure the message is not empty
        if not message:
            print(f"[Thread for {addr}] Empty request, closing connection.")
            connectionSocket.close()
            return

        print(f"[Thread for {addr}] Received request: {message.splitlines()[0]}")

        # Parse the filename from the request
        filename = message.split()[1]
        
        # Open the file, stripping the leading '/'
        f = open(filename[1:])
        
        # Read the entire content of the file
        outputdata = f.read()
        f.close() # Close the file

        # Send the "200 OK" status line, followed by a blank line
        connectionSocket.send('HTTP/1.1 200 OK\r\n\r\n'.encode())

        # Send the content of the requested file
        for i in range(0, len(outputdata)):
            connectionSocket.send(outputdata[i].encode())
        connectionSocket.send("\r\n".encode())
        
        print(f"[Thread for {addr}] Sent file: {filename[1:]}")

    except IOError:
        # Send response message for file not found
        print(f"[Thread for {addr}] Error: File not found: {filename[1:]}")
        response = 'HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>404 Not Found</h1></body></html>'
        connectionSocket.send(response.encode())
    
    except Exception as e:
        print(f"[Thread for {addr}] An error occurred: {e}")

    finally:
        # Close client socket
        connectionSocket.close()
        print(f"[Thread for {addr}] Connection closed.")

# --- Main Server Logic ---

# Prepare a sever socket
serverSocket = socket(AF_INET, SOCK_STREAM)
# This allows reusing the port address immediately after closing
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) 

serverPort = 6789
serverSocket.bind(('', serverPort))
serverSocket.listen(5) # Increase backlog to 5 for a multithreaded server
print(f"Main server listening on port {serverPort}...")

try:
    while True:
        # Establish the connection
        # The main thread BLOCKS here, waiting for a new connection
        print("\nMain thread: Ready to serve, waiting for connection...")
        connectionSocket, addr = serverSocket.accept()
        print(f"Main thread: Accepted connection from {addr}")

        # Create a new thread to handle this client
        # - target: the function the thread will run
        # - args: the arguments to pass to that function (must be a tuple)
        client_thread = threading.Thread(target=handle_client, args=(connectionSocket, addr))
        
        # Start the new thread. 
        # The main loop will immediately continue and go back to serverSocket.accept()
        client_thread.start()

except KeyboardInterrupt:
    print("\nShutting down server due to KeyboardInterrupt (Ctrl+C)...")
except Exception as e:
    print(f"An error occurred in the main thread: {e}")
finally:
    serverSocket.close()
    sys.exit() # Terminate the program
