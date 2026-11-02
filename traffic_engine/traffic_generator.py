#!/usr/bin/env python3
"""
Dynamic Routing Optimization in SDN
Component: Traffic Generator (Elephant vs. Mice Flow Synthesis)
Author: Bratin Roy (Roll: 12200123042)
Branch: feature/network-topology-and-chaos

Description:
    Simulates real-world data center / cloud traffic patterns:
    1. Mice Flows: Continuous low-bandwidth latency-sensitive flows (HTTP/DNS simulation).
    2. Elephant Flows: Sudden high-bandwidth bursts (18 Mbps on a 15 Mbps link)
       to trigger congestion and evaluate dynamic rerouting.
"""

import time
import subprocess
import argparse
import sys

def run_iperf_server(host_name="h2"):
    """Starts iperf3 server on destination host."""
    print(f"[*] Starting iperf3 server on {host_name}...")
    cmd = f"sudo mn -m --target {host_name} iperf3 -s -D"
    subprocess.run(cmd, shell=True)

def inject_mice_flow(src="h1", dst_ip="10.0.0.2", duration=30):
    """Generates continuous lightweight latency-sensitive packets."""
    print(f"[+] Injecting Mice Flow from {src} to {dst_ip} (Duration: {duration}s)...")
    # Low-rate UDP ping / packet stream (500 Kbps)
    cmd = f"sudo mn -m --target {src} iperf3 -c {dst_ip} -u -b 500K -t {duration} &"
    subprocess.Popen(cmd, shell=True)

def inject_elephant_flow(src="h1", dst_ip="10.0.0.2", bandwidth="18M", duration=20):
    """
    Generates a high-bandwidth burst that exceeds link capacity (15 Mbps),
    causing buffer overflow unless the controller detours it dynamically.
    """
    print(f"[!] INJECTING ELEPHANT FLOW: {src} -> {dst_ip} | Rate: {bandwidth} | Duration: {duration}s")
    cmd = f"sudo mn -m --target {src} iperf3 -c {dst_ip} -u -b {bandwidth} -t {duration}"
    subprocess.run(cmd, shell=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SDN Dynamic Traffic Injector")
    parser.add_argument("--mode", choices=["mice", "elephant", "mixed"], default="mixed",
                        help="Traffic profile to inject")
    parser.add_argument("--rate", default="18M", help="Elephant flow bandwidth rate (e.g., 18M)")
    parser.add_argument("--duration", type=int, default=25, help="Burst duration in seconds")
    args = parser.parse_args()

    print("==================================================")
    print("      SDN TRAFFIC SYNTHESIS & STRESS ENGINE       ")
    print("==================================================")

    if args.mode == "mice":
        inject_mice_flow(duration=args.duration)
    elif args.mode == "elephant":
        inject_elephant_flow(bandwidth=args.rate, duration=args.duration)
    elif args.mode == "mixed":
        # Launch background mice flows first, then inject elephant flow after 5 seconds
        inject_mice_flow(duration=args.duration + 5)
        print("[*] Normal traffic running. Injecting elephant congestion spike in 5 seconds...")
        time.sleep(5)
        inject_elephant_flow(bandwidth=args.rate, duration=args.duration)
