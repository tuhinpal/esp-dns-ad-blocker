import socket
import time

class DNSSocket:
    def __init__(self, blocklist_manager, upstream=("1.1.1.1", 53)):
        self.blocklist_manager = blocklist_manager
        self.upstream = upstream
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", 53))
        self.sock.setblocking(False)
        self.cache = {}  # Cache: {query_bytes: (response_bytes, timestamp)}
        self.cache_ttl = 60  # 1 minute in seconds
        self.last_cleanup = time.time()
        self.cleanup_interval = 60  # Cleanup every 60 seconds
    
    def get_socket(self):
        """Return the socket"""
        return self.sock
    
    def parse_domain(self, data):
        """Parse domain from DNS query"""
        i = 12
        parts = []
        while i < len(data) and data[i] != 0:
            ln = data[i]
            i += 1
            if i + ln > len(data):
                break
            parts.append(data[i:i+ln].decode())
            i += ln
        return ".".join(parts)
    
    def blocked_response(self, query):
        """Return DNS blocked response"""
        tid = query[:2]
        flags = b"\x81\x80"
        counts = b"\x00\x01\x00\x01\x00\x00\x00\x00"
        header = tid + flags + counts
        question = query[12:]
        answer = b"\xc0\x0c\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04\x00\x00\x00\x00"
        return header + question + answer
    
    def servfail_response(self, query):
        """Return DNS SERVFAIL response"""
        tid = query[:2]
        flags = b"\x81\x82"  # Response + SERVFAIL
        counts = b"\x00\x01\x00\x00\x00\x00\x00\x00"
        header = tid + flags + counts
        question = query[12:]
        return header + question
    
    def get_cache_key(self, query):
        """Use query without transaction ID as cache key"""
        return query[2:]  # Skip transaction ID (first 2 bytes)
    
    def cleanup_cache(self):
        """Remove all expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if current_time - timestamp >= self.cache_ttl
        ]
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            print(f"  -> Cleaned {len(expired_keys)} expired cache entries")
        
        self.last_cleanup = current_time
    
    def get_from_cache(self, query):
        """Retrieve response from cache (no expiry check)"""
        cache_key = self.get_cache_key(query)
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            # Update transaction ID to match current query
            return query[:2] + response[2:]
        return None
    
    def add_to_cache(self, query, response):
        """Add response to cache"""
        cache_key = self.get_cache_key(query)
        self.cache[cache_key] = (response, time.time())
    
    def forward(self, query):
        """Forward DNS query with timeout protection"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2.0)  # 2 second timeout
        try:
            s.sendto(query, self.upstream)
            data, _ = s.recvfrom(512)
            s.close()
            return data
        except socket.timeout:
            print(f"  -> TIMEOUT: Upstream DNS not responding")
            s.close()
            return None
        except Exception as e:
            print(f"  -> ERROR: {e}")
            s.close()
            return None
    
    def handle_periodic_tasks(self):
        """Handle periodic maintenance tasks"""
        current_time = time.time()
        
        # Periodic cache cleanup
        if current_time - self.last_cleanup >= self.cleanup_interval:
            self.cleanup_cache()
    
    def handle_request(self):
        """Handle DNS request"""
        try:
            data, addr = self.sock.recvfrom(512)
            domain = self.parse_domain(data)
            print("DNS:", domain)
            
            if self.blocklist_manager.is_blocked(domain):
                resp = self.blocked_response(data)
                print(f"  -> BLOCKED")
            else:
                # Check cache first
                cached_resp = self.get_from_cache(data)
                if cached_resp:
                    resp = cached_resp
                    print(f"  -> CACHED")
                else:
                    resp = self.forward(data)
                    if resp is None:
                        # Timeout or error - return SERVFAIL
                        resp = self.servfail_response(data)
                    else:
                        self.add_to_cache(data, resp)
                        print(f"  -> FORWARDED")
            
            self.sock.sendto(resp, addr)
        except OSError:
            pass  # No data available

