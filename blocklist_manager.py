class BlocklistManager:
    def __init__(self, filename="blocklist.txt"):
        self.filename = filename
        self.blocklist = set()
        self.load()
    
    def load(self):
        """Load blocklist from file"""
        try:
            with open(self.filename, 'r') as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):  # Skip empty lines and comments
                        self.blocklist.add(domain)
            print(f"Loaded {len(self.blocklist)} domains from {self.filename}")
        except OSError:
            print(f"No existing blocklist found, creating new {self.filename}")
            self.save()  # Create empty file
    
    def save(self):
        """Save entire blocklist to file"""
        try:
            with open(self.filename, 'w') as f:
                for domain in sorted(self.blocklist):
                    f.write(domain + '\n')
            print(f"Saved {len(self.blocklist)} domains to {self.filename}")
        except OSError as e:
            print(f"Error saving blocklist: {e}")
    
    def add(self, domain):
        """Add domain to blocklist and append to file"""
        domain = domain.strip().lower()
        if domain and domain not in self.blocklist:
            self.blocklist.add(domain)
            try:
                with open(self.filename, 'a') as f:
                    f.write(domain + '\n')
                print(f"Added {domain} to blocklist")
                return True
            except OSError as e:
                print(f"Error adding to file: {e}")
                self.blocklist.remove(domain)  # Rollback
                return False
        return False
    
    def remove(self, domain):
        """Remove domain from blocklist and rewrite file"""
        domain = domain.strip().lower()
        if domain in self.blocklist:
            self.blocklist.remove(domain)
            self.save()  # Rewrite entire file
            print(f"Removed {domain} from blocklist")
            return True
        return False
    
    def is_blocked(self, domain):
        """Check if domain is in blocklist"""
        return domain.lower() in self.blocklist
    
    def get_all(self):
        """Get all blocked domains"""
        return sorted(list(self.blocklist))
    
    def clear(self):
        """Clear all domains from blocklist"""
        self.blocklist.clear()
        self.save()
        print("Blocklist cleared")
    
