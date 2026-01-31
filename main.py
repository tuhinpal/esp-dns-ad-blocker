import time
import _thread
from wifi_manager import WiFiManager
from blocklist_manager import BlocklistManager
from dns_socket import DNSSocket
from web_socket import WebSocket

# Configuration
SSID = "<SSID_2.5G>"
PASSWORD = "<PASSWORD_2.5G>"
BLOCKLIST_FILE = "blocklist.txt"

# Global flag for graceful shutdown
running = True

def dns_thread(dns):
    """DNS server thread"""
    print("DNS thread started")
    while running:
        try:
            dns.handle_request()
            time.sleep(0.001)
        except Exception as e:
            print(f"DNS Error: {e}")
            time.sleep(0.1)

def web_thread(web):
    """Web server thread"""
    print("Web thread started")
    while running:
        try:
            web.handle_request()
            time.sleep(0.001)
        except Exception as e:
            print(f"Web Error: {e}")
            time.sleep(0.1)

def periodic_thread(dns):
    """Periodic maintenance thread"""
    print("Periodic task thread started")
    while running:
        try:
            time.sleep(10)
            dns.handle_periodic_tasks()
        except Exception as e:
            print(f"Periodic Error: {e}")

def main():
    global running
    
    # Initialize WiFi
    print("Connecting to WiFi...")
    wifi = WiFiManager(SSID, PASSWORD)
    wifi.connect()
    
    # Initialize Blocklist (loads from file automatically)
    blocklist = BlocklistManager(BLOCKLIST_FILE)
    
    # Initialize DNS and Web sockets
    dns = DNSSocket(blocklist)
    web = WebSocket(blocklist, wifi)
    
    print("\n" + "="*50)
    print("DNS Blocker Server Started!")
    print("="*50)
    print(f"Web interface: http://{wifi.get_ip()}:8080")
    print(f"DNS server: {wifi.get_ip()}:53")
    print("="*50 + "\n")
    
    # Start threads
    _thread.start_new_thread(dns_thread, (dns,))
    _thread.start_new_thread(web_thread, (web,))
    _thread.start_new_thread(periodic_thread, (dns,))
    
    # Main thread - keep alive and handle shutdown
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        running = False
        time.sleep(2)
        print("Shutdown complete")

if __name__ == "__main__":
    main()

