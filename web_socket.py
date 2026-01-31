import socket

class WebSocket:
    def __init__(self, blocklist_manager, wifi_manager, port=8080):
        self.blocklist_manager = blocklist_manager
        self.wifi_manager = wifi_manager
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(5)
        self.sock.setblocking(False)
    
    def get_socket(self):
        return self.sock
    
    def handle_request(self):
        try:
            conn, addr = self.sock.accept()
            conn.setblocking(True)
            print(f"HTTP connection from {addr}")
            
            try:
                req = conn.recv(1024).decode()
                print(f"Request: {req.split()[0:2] if req else 'empty'}")
                
                # Parse request
                if not req:
                    conn.close()
                    return
                
                lines = req.split('\r\n')
                if lines:
                    request_line = lines[0].split()
                    if len(request_line) >= 2:
                        method = request_line[0]
                        path = request_line[1]
                        
                        response = self.route_request(method, path, req)
                        conn.send(response.encode())
            finally:
                conn.close()
        except OSError:
            pass  # No connection available
    
    def route_request(self, method, path, full_request):
        if path == "/" or path == "/index.html" or path == "/blocklist":
            return self.blocklist_page()
        elif path.startswith("/add?domain="):
            domain = path.split("=")[1]
            self.blocklist_manager.add(domain)
            return self.redirect_response("/blocklist")
        elif path.startswith("/remove?domain="):
            domain = path.split("=")[1]
            self.blocklist_manager.remove(domain)
            return self.redirect_response("/blocklist")
        else:
            return self.not_found()
        
    def blocklist_page(self):
        blocked_domains = self.blocklist_manager.get_all()
        domain_list = "".join([f"<li>{d} <a href='/remove?domain={d}'>Remove</a></li>" 
                               for d in blocked_domains])
        
        body = """<html>
<head><title>Blocklist</title></head>
<body>
<h1>Blocked Domains</h1>
<ul>{}</ul>
<form action="/add" method="get">
    <input type="text" name="domain" placeholder="domain.com">
    <input type="submit" value="Add">
</form>
</body>
</html>""".format(domain_list if domain_list else "<li>No domains blocked</li>")
        
        return self.http_response(body)
    
    def not_found(self):
        body = "<html><body><h1>404 Not Found</h1></body></html>"
        return "HTTP/1.1 404 Not Found\r\n" + self.headers(body) + body
    
    def redirect_response(self, location):
        return f"HTTP/1.1 302 Found\r\nLocation: {location}\r\n\r\n"
    
    def http_response(self, body):
        return "HTTP/1.1 200 OK\r\n" + self.headers(body) + body
    
    def headers(self, body):
        return (
            "Content-Type: text/html\r\n"
            f"Content-Length: {len(body)}\r\n"
            "Connection: close\r\n\r\n"
        )

