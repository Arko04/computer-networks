# HW2 – HTTP Web Server

A small web server written directly on top of TCP sockets, with no HTTP library, plus a minimal client. Based on the Kurose & Ross socket-programming lab.

| File | Description |
|------|-------------|
| `server.py` | Single-threaded server: parses the request line, serves the file with `200 OK`, or returns `404 Not Found` |
| `multithreaded_server.py` | Same server, but each connection is handled in its own thread, so clients are served in parallel |
| `client.py` | HTTP client: `python3 client.py <host> <port> <file>` |
| `HelloWorld.html` | Sample page to serve |
| `report.pdf` | Report with the written answers and screenshots (Persian) |

## Run

```bash
python3 multithreaded_server.py          # listens on port 6789
# in another terminal / browser:
python3 client.py 127.0.0.1 6789 HelloWorld.html
curl -i http://127.0.0.1:6789/HelloWorld.html   # 200 OK
curl -i http://127.0.0.1:6789/missing.html      # 404 Not Found
```
