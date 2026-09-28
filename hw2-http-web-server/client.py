#import socket module
from socket import *
import sys # For reading command-line arguments

# Check if all required arguments are provided
if len(sys.argv) != 4:
    print("Usage: python client.py server_host server_port filename")
    sys.exit()

# Parse command-line arguments
server_host = sys.argv[1]
# Convert port from string to integer
try:
    server_port = int(sys.argv[2])
except ValueError:
    print(f"Error: server_port '{sys.argv[2]}' must be an integer.")
    sys.exit()
    
filename = sys.argv[3]

# --- 1. Create a client socket ---
# AF_INET = Use IPv4
# SOCK_STREAM = Use TCP
try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    print(f"Socket created...")
except error as e:
    print(f"Error creating socket: {e}")
    sys.exit()

# --- 2. Connect to the server ---
try:
    print(f"Connecting to {server_host} on port {server_port}...")
    clientSocket.connect((server_host, server_port))
    print("Connection successful.")
except error as e:
    print(f"Error connecting to server: {e}")
    sys.exit()

# --- 3. Send the HTTP GET request ---
# We must format a proper HTTP 1.1 GET request.
# It needs:
# 1. The request line: GET /<filename> HTTP/1.1
# 2. The Host header: Host: <server_host>
# 3. A blank line (\r\n) to end the headers
# Note: We add a '/' before the filename
request = f"GET /{filename} HTTP/1.1\r\nHost: {server_host}\r\n\r\n"

try:
    clientSocket.send(request.encode())
    print(f"Sent GET request for: /{filename}")
except error as e:
    print(f"Error sending data: {e}")
    clientSocket.close()
    sys.exit()

# --- 4. Receive and print the server's response ---
print("\n--- Server Response ---")
response = ""
while True:
    # Receive data in chunks of 1024 bytes
    data = clientSocket.recv(1024)
    if not data:
        # If no more data is received, the server has closed the connection
        break
    
    # Decode the received bytes into a string (using 'utf-8')
    # Use 'ignore' to prevent errors on strange characters
    response_chunk = data.decode('utf-8', 'ignore')
    print(response_chunk, end='') # Print the chunk without adding a new line

print("\n--- End of Response ---")

# --- 5. Close the socket ---
clientSocket.close()
print("Connection closed.")

"""
### How to Run This Code

1.  **Save:** Save the code above as `client.py`.
2.  **Run Server:** Make sure your `server.py` is running in one terminal.
3.  **Run Client:** Open a *second* terminal and run the `client.py` script, providing the three required arguments.

**Example (if your server is on the same machine):**
Your server is running. In the second terminal, you would type:

```bash
python client.py 127.0.0.1 6789 HelloWorld.html
```
*(Use `127.0.0.1` (or `localhost`) if the client and server are on the same computer. If they are on different computers, use the server's local IP address, like `172.17.70.236`.)*

**Example (requesting a file that doesn't exist):**

```bash
python client.py 127.0.0.1 6789 MissingFile.html
"""