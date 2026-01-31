# ESP DNS AD Blocker

A lightweight DNS server with ad-blocking capabilities running on ESP32 Rpi Pico W microcontrollers using MicroPython. Block unwanted domains at the network level with a simple web interface for management.

## Features

- **DNS Server**: Custom DNS server with domain blocking capabilities
- **Web Interface**: Manage your blocklist through a simple web UI (port 8080)
- **DNS Caching**: Improves performance by caching DNS responses with automatic cleanup.
- **Multi-threaded**: Handles DNS and web requests concurrently
- **Persistent Storage**: Blocklist is saved to flash memory
- **Upstream DNS Forwarding**: Uses Cloudflare DNS (1.1.1.1) by default

## Hardware Requirements

- ESP32 or Pico W development board
- USB cable for programming
- WiFi network connection

## Software Requirements

- **Thonny IDE**
- **MicroPython firmware**

## Installation

### Step 1: Install Thonny IDE

1. Download Thonny from [https://thonny.org](https://thonny.org)
2. Install it on your computer (Windows, macOS, or Linux)
3. Launch Thonny

### Step 2: Flash MicroPython Firmware

In Thonny:

- Click **Tools → Options**
- Select the **Interpreter** tab
- Choose **MicroPython (ESP32)** from the dropdown
- Click **Install or update MicroPython**
- Select your USB port (In mac it is usually `USB to UART Bridge`, please see the below guide)
- Click **Install or update MicroPython**
- Wait for the process to complete

See this for [full guide](https://randomnerdtutorials.com/getting-started-thonny-micropython-python-ide-esp32-esp8266/)

### Step 3: Verify Connection

1. In Thonny, click the **Stop/Restart** button (red circle with X)
2. You should see the MicroPython REPL prompt (`>>>`) in the Shell window at the bottom
3. Try typing: `print("Hello from ESP32!")`

### Step 4: Upload Project Files

1. In Thonny, open the file you want to upload
2. Click **File → Save As...**
3. Select **MicroPython device**
4. Save the file to the root directory of the device

**Upload these files in order:**

1. `wifi_manager.py`
2. `blocklist_manager.py`
3. `dns_socket.py`
4. `web_socket.py`
5. `blocklist.txt`
6. `main.py`

### Step 5: Configure WiFi Credentials

1. Open `main.py` on your ESP device (from Thonny's file browser)
2. Modify lines 9-10:
   ```python
   SSID = "YourWiFiName"
   PASSWORD = "YourWiFiPassword"
   ```
3. Save the file (Ctrl+S or Cmd+S)

### Step 6: Run the Application

#### Option A: Manual Run (for testing)

1. Make sure `main.py` is open in Thonny
2. Click the **Run** button (green arrow) or press F5
3. Watch the Shell output for connection status

#### Option B: Auto-run on Boot (recommended)

1. Rename `main.py` to `boot.py` on the device
   - Or create a simple `boot.py` that imports main:
   ```python
   import main
   ```
2. Press the **RST** button on your ESP board
3. The application will start automatically

## Usage

### Accessing the Web Interface

Once the ESP is running, the Shell output will show:

```
==================================================
DNS Blocker Server Started!
==================================================
Web interface: http://192.168.1.XXX:8080
DNS server: 192.168.1.XXX:53
==================================================
```

1. Open your web browser
2. Navigate to `http://[ESP_IP_ADDRESS]:8080`
3. You'll see the blocklist management page

### Managing the Blocklist

**Add a domain:**

1. Enter the domain name (e.g., `ads.example.com`)
2. Click **Add**
3. The domain is immediately blocked and saved to flash

**Remove a domain:**

1. Click **Remove** next to the domain
2. The domain is unblocked and removed from flash

### Configure Your Device DNS

To use the ESP DNS blocker on your devices:

**Option 1: Per Device**

- Go to WiFi settings on your phone/computer
- Manually set DNS to your ESP's IP address

**Option 2: Router-wide**

- Log into your router admin panel
- Set the primary DNS to your ESP's IP address
- All devices on the network will use the blocker

## Configuration Options

### Change Upstream DNS Server

Edit `dns_socket.py`, line 5:

```python
def __init__(self, blocklist_manager, upstream=("1.1.1.1", 53)):
```

Popular alternatives:

- Google DNS: `("8.8.8.8", 53)`
- OpenDNS: `("208.67.222.222", 53)`

### Change Web Server Port

Edit `web_socket.py`, line 4:

```python
def __init__(self, blocklist_manager, wifi_manager, port=8080):
```

### Adjust Cache TTL

Edit `dns_socket.py`, line 12:

```python
self.cache_ttl = 60  # seconds
```

## Performance Notes

I don't know, Please test and let me know.

## Adding Bulk Blocklists

To add many domains at once:

1. Edit `blocklist.txt` on your computer with one domain per line:

   ```
   ads.example.com
   tracker.example.net
   analytics.example.org
   ```

2. Upload the updated `blocklist.txt` to the ESP using Thonny

3. Restart the ESP (press RST button)

**Popular blocklist sources:**

- https://github.com/StevenBlack/hosts
- https://oisd.nl
- https://adaway.org

Note: Convert host file format (`0.0.0.0 domain.com`) to just `domain.com`

## Security Considerations

- This is a basic DNS blocker, not a firewall
- It only blocks DNS resolution, not IP-based connections
- Devices can bypass it if they use hardcoded DNS servers
- The web interface has no authentication
- Consider using HTTPS for the web interface in production

## Contributing

Feel free to enhance this project! Some ideas:

- Add authentication to web interface
- Implement HTTPS support
- Add DNS-over-HTTPS upstream support
- Statistics dashboard
- Whitelist functionality
- Regex pattern matching (ESP probably not that powerful to handle this)

## License

MIT License. Feel free to use and modify!

## Credits

Built with MicroPython.

### Made by Tuhin in Weekend 🚀
