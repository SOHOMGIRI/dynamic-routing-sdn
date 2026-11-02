#!/usr/bin/env python3
"""
Dynamic Routing Optimization in SDN
Component: Chaos Link Failure & Recovery Injector
Author: Bratin Roy (Roll: 12200123042)
Branch: feature/network-topology-and-chaos

Description:
    Simulates sudden physical trunk link breakage (cable cuts, switch port failures)
    and subsequent link recovery to evaluate controller failover speed and packet survival.
"""

import time
import subprocess
import argparse
import sys

def set_link_status(switch="s1", port="s1-eth5", status="down"):
    """Brings an Open vSwitch port down or up to simulate physical link failure."""
    action = "down" if status.lower() == "down" else "up"
    print(f"[!] CHAOS EVENT: Setting {switch} port {port} to [{action.upper()}]...")
    cmd = f"sudo ip link set dev {port} {action}"
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"[✓] Port {port} successfully set to {action.upper()}.")
    else:
        print(f"[X] Error altering port: {res.stderr.strip()}")

def run_chaos_test(switch="s1", port="s1-eth5", down_duration=10):
    """
    Executes a complete failure-and-recovery cycle:
    1. Runs normally for 5 seconds.
    2. Severs the link for down_duration seconds.
    3. Restores the link.
    """
    print("==================================================")
    print("        SDN CHAOS LINK FAILURE INJECTOR           ")
    print("==================================================")
    print(f"[*] Starting test cycle on target link: {port}")
    print("[*] Normal operations for 5 seconds...")
    time.sleep(5)

    print(f"\n[>>>] INITIATING SUDDEN LINK SEVERANCE at {time.strftime('%X')}")
    set_link_status(switch=switch, port=port, status="down")
    
    print(f"[*] Link severed. Observing failover behavior for {down_duration} seconds...")
    time.sleep(down_duration)

    print(f"\n[<<<] INITIATING LINK RESTORATION at {time.strftime('%X')}")
    set_link_status(switch=switch, port=port, status="up")
    print("[✓] Chaos test cycle completed. Link returned to service.\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SDN Chaos Link Severance Tool")
    parser.add_argument("--switch", default="s1", help="Switch hosting the target link (e.g., s1)")
    parser.add_argument("--port", default="s1-eth5", help="Port interface name to sever (e.g., s1-eth5)")
    parser.add_argument("--duration", type=int, default=10, help="Downtime duration in seconds")
    args = parser.parse_args()

    run_chaos_test(switch=args.switch, port=args.port, down_duration=args.duration)
