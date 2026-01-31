import network
import time

class WiFiManager:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)
        self.ip = None
    
    def connect(self):
        self.wlan.active(True)
        self.wlan.connect(self.ssid, self.password)
        
        print("Connecting WiFi...")
        while not self.wlan.isconnected():
            time.sleep(0.5)
        
        self.ip = self.wlan.ifconfig()[0]
        print("Connected IP:", self.ip)
        return self.ip
    
    def get_ip(self):
        return self.ip
    
    def is_connected(self):
        return self.wlan.isconnected()

