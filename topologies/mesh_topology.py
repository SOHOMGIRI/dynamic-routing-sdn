#!/usr/bin/env python3
"""
Dynamic Routing Optimization in SDN
Component: Custom 6-Switch Multi-Path Mesh Topology
Author: Bratin Roy (Roll: 12200123042)
Branch: feature/network-topology-and-chaos

Description:
    Creates a redundant 6-switch multi-path mesh topology in Mininet.
    Uses TCLink to emulate realistic link constraints (bandwidth, latency, queue sizes).
    Connects switches to an external OpenFlow 1.3 Ryu SDN Controller.
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from functools import partial
import sys
import time

class DynamicMeshTopo(Topo):
    """
    Topology Architecture:
    
                     [h1] (10.0.0.1)
                       │
                     (s1)═════════════════════(s2)───[h2] (10.0.0.2)
                     ╱  ╲                     ╱  ╲
                    ╱    ╲                   ╱    ╲
                  (s3)───(s4)──────────────(s5)───(s6)
                           │                │
                     [h3] (10.0.0.3)  [h4] (10.0.0.4)

    - Primary Path: s1 <---> s2 (Direct link, 15 Mbps, 5ms delay)
    - Detour Path 1: s1 <-> s3 <-> s4 <-> s5 <-> s2 (Multi-hop high capacity)
    - Detour Path 2: s1 <-> s4 <-> s5 <-> s6 <-> s2
    """
    def build(self):
        info("*** Adding 6 Open vSwitches (OpenFlow 1.3)...\n")
        s1 = self.addSwitch('s1', dpid='0000000000000001')
        s2 = self.addSwitch('s2', dpid='0000000000000002')
        s3 = self.addSwitch('s3', dpid='0000000000000003')
        s4 = self.addSwitch('s4', dpid='0000000000000004')
        s5 = self.addSwitch('s5', dpid='0000000000000005')
        s6 = self.addSwitch('s6', dpid='0000000000000006')

        info("*** Adding 4 End Hosts...\n")
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')

        info("*** Connecting Hosts to Access Switches...\n")
        self.addLink(h1, s1, bw=100, delay='1ms')
        self.addLink(h2, s2, bw=100, delay='1ms')
        self.addLink(h3, s4, bw=100, delay='1ms')
        self.addLink(h4, s5, bw=100, delay='1ms')

        info("*** Building Core Inter-Switch Mesh Links...\n")
        # Direct trunk (Candidate for congestion & severance)
        self.addLink(s1, s2, bw=15, delay='5ms', max_queue_size=100)

        # Redundant mesh pathways with diverse metrics
        self.addLink(s1, s3, bw=25, delay='3ms')
        self.addLink(s1, s4, bw=20, delay='6ms')
        self.addLink(s3, s4, bw=25, delay='2ms')
        self.addLink(s4, s5, bw=30, delay='5ms')
        self.addLink(s2, s5, bw=20, delay='6ms')
        self.addLink(s2, s6, bw=25, delay='3ms')
        self.addLink(s5, s6, bw=25, delay='2ms')

def start_network():
    """Starts the Mininet network and hooks to Ryu controller."""
    topo = DynamicMeshTopo()
    ovs13 = partial(OVSSwitch, protocols='OpenFlow13')

    net = Mininet(
        topo=topo,
        switch=ovs13,
        controller=None,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )

    info("*** Connecting to Remote Ryu SDN Controller at 127.0.0.1:6653...\n")
    c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', port=6653)

    net.start()
    net.staticArp()
    info("*** Waiting 2s for Ryu LLDP discovery to map redundant mesh links...\n")
    time.sleep(2)
    info("*** Mesh Network Initialized Successfully.\n")
    info("*** Type 'pingall' to test connectivity or 'exit' to quit.\n")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    start_network()
