import socket

def is_port_open(host, port):
    try:
        with socket.create_connection((host, port), timeout=5):
            print(f"Port {port} auf {host} ist offen.")
            return True
    except (socket.timeout, ConnectionRefusedError):
        print(f"Port {port} auf {host} ist geschlossen oder nicht erreichbar.")
        return False

host = "ora-02.db.lab.etf.unsa.ba"
port = 27017
is_port_open(host, port)