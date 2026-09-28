"""
Generate a synthetic offline PCAP file for SIH26148 offline PCAP forensic analysis.
Complies with standard libpcap 2.4 format.
"""

import os
import struct
import time

def create_sample_pcap(filepath: str):
    # PCAP Global Header: magic (0xa1b2c3d4), v2.4, thiszone=0, sigfigs=0, snaplen=65535, network=1 (Ethernet)
    global_hdr = struct.pack("!IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)

    packets_data = []
    base_time = int(time.time()) - 3600

    # Helper: build IPv4 + TCP/UDP Ethernet frame
    def make_eth_ip_udp(src_ip, dst_ip, src_port, dst_port, payload_bytes, ts):
        # Eth header: dst_mac (6), src_mac (6), ethertype=0x0800 (IPv4)
        eth = b"\x00\x0c\x29\x4b\x82\x11\x00\x50\x56\xc0\x00\x08\x08\x00"
        
        # IP header
        ip_len = 20 + 8 + len(payload_bytes)
        ip = struct.pack("!BBHHHBBH4s4s",
            0x45, 0, ip_len, 0x1234, 0x4000, 64, 17, 0,
            bytes(map(int, src_ip.split('.'))),
            bytes(map(int, dst_ip.split('.')))
        )
        
        # UDP header
        udp_len = 8 + len(payload_bytes)
        udp = struct.pack("!HHHH", src_port, dst_port, udp_len, 0)
        
        frame = eth + ip + udp + payload_bytes
        hdr = struct.pack("!IIII", ts, 0, len(frame), len(frame))
        return hdr + frame

    def make_eth_ip_tcp(src_ip, dst_ip, src_port, dst_port, payload_bytes, ts):
        eth = b"\x00\x0c\x29\x4b\x82\x11\x00\x50\x56\xc0\x00\x08\x08\x00"
        ip_len = 20 + 20 + len(payload_bytes)
        ip = struct.pack("!BBHHHBBH4s4s",
            0x45, 0, ip_len, 0x5678, 0x4000, 64, 6, 0,
            bytes(map(int, src_ip.split('.'))),
            bytes(map(int, dst_ip.split('.')))
        )
        # TCP header (20 bytes)
        tcp = struct.pack("!HHIIBBHHH",
            src_port, dst_port, 1000, 2000, 0x50, 0x18, 65535, 0, 0
        )
        frame = eth + ip + tcp + payload_bytes
        hdr = struct.pack("!IIII", ts, 0, len(frame), len(frame))
        return hdr + frame

    # Packet 1: DNS query for malicious-telemetry-sync.xyz
    p1 = make_eth_ip_udp("192.168.1.105", "1.1.1.1", 53120, 53, b"\x12\x34\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00\x09malicious\x0etelemetry-sync\x03xyz\x00\x00\x01\x00\x01", base_time)
    
    # Packet 2: DNS response with 198.51.100.45
    p2 = make_eth_ip_udp("1.1.1.1", "192.168.1.105", 53, 53120, b"\x12\x34\x81\x80\x00\x01\x00\x01\x00\x00\x00\x00\x09malicious\x0etelemetry-sync\x03xyz\x00\x00\x01\x00\x01\xc0\x0c\x00\x01\x00\x01\x00\x00\x01\x2c\x00\x04\xc6\x33\x64\x2d", base_time + 1)
    
    # Packet 3: HTTP GET request to stager
    p3 = make_eth_ip_tcp("192.168.1.105", "203.0.113.88", 52110, 80, b"GET /stage2.bin HTTP/1.1\r\nHost: 203.0.113.88\r\nUser-Agent: Mozilla/5.0\r\n\r\n", base_time + 3)
    
    # Packet 4: TCP C2 Beacon packet to port 4444
    p4 = make_eth_ip_tcp("192.168.1.105", "198.51.100.45", 51442, 4444, b"BEACON_HEARTBEAT_SESSION_4820_WS-FIN-04", base_time + 5)

    with open(filepath, "wb") as f:
        f.write(global_hdr)
        f.write(p1)
        f.write(p2)
        f.write(p3)
        f.write(p4)

if __name__ == "__main__":
    os.makedirs("sample_data", exist_ok=True)
    create_sample_pcap("sample_data/sample_traffic.pcap")
    print("Created sample_data/sample_traffic.pcap successfully.")
