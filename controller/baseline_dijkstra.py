#!/usr/bin/env python3
"""
Dynamic Routing Optimization in SDN
Component: Classical Static Shortest-Path Baseline (OSPF / Dijkstra Equivalent)
Author: Sohom Giri (Roll: 12200123157) - Team Lead & Core Engine Architect
Branch: feature/adaptive-routing-engine

Description:
    Implements classical static shortest path routing (OSPF equivalent).
    Demonstrates the flaws of traditional algorithms:
    - Uses fixed static hop count metrics (Cost = 1.0 per link).
    - Congestion-Blind: Funnels all flows along the direct trunk link even when saturated.
    - Used as the empirical benchmark against the Adaptive Dynamic Routing Controller.
"""

import json
import os
import time
import networkx as nx

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.topology import event
from ryu.topology.api import get_switch, get_link
from ryu.lib import hub

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "analytics", "logs")
STATE_FILE = os.path.join(LOG_DIR, "live_network_state.json")

class StaticBaselineController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(StaticBaselineController, self).__init__(*args, **kwargs)
        self.topology_api_app = self
        self.network_graph = nx.DiGraph()
        self.datapaths = {}
        self.mac_to_port = {}
        self.host_locations = {'00:00:00:00:00:01': (1, 1), '00:00:00:00:00:02': (2, 1), '00:00:00:00:00:03': (4, 1), '00:00:00:00:00:04': (5, 1)}

        os.makedirs(LOG_DIR, exist_ok=True)
        self.logger.info("=====================================================")
        self.logger.info("   CLASSICAL STATIC BASELINE (OSPF / Hop-Count)      ")
        self.logger.info("=====================================================")
        self.discovery_thread = hub.spawn(self._discovery_loop)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        self.datapaths[datapath.id] = datapath
        self.mac_to_port.setdefault(datapath.id, {})

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0, match=match, instructions=inst)
        datapath.send_msg(mod)

    def _discovery_loop(self):
        while True:
            switch_list = get_switch(self.topology_api_app, None)
            switches = [s.dp.id for s in switch_list]
            self.network_graph.add_nodes_from(switches)

            links = get_link(self.topology_api_app, None)
            for l in links:
                # Static routing: every link weight = 1.0 (Hop Count)
                self.network_graph.add_edge(l.src.dpid, l.dst.dpid, port=l.src.port_no, weight=1.0)
                self.network_graph.add_edge(l.dst.dpid, l.src.dpid, port=l.dst.port_no, weight=1.0)
            hub.sleep(2)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return

        src_mac = eth.src
        dst_mac = eth.dst
        self.host_locations[src_mac] = (dpid, in_port)

        if dst_mac in self.host_locations:
            dst_dpid, dst_port = self.host_locations[dst_mac]
            try:
                # Blind shortest path (ignores traffic/congestion)
                path = nx.shortest_path(self.network_graph, source=dpid, target=dst_dpid, weight='weight')
            except Exception:
                path = None

            if path and len(path) > 1:
                next_hop = path[1]
                out_port = self.network_graph[dpid][next_hop]['port']
            else:
                out_port = dst_port if dpid == dst_dpid else datapath.ofproto.OFPP_FLOOD
        else:
            out_port = 1

        actions = [parser.OFPActionOutput(out_port)]
        if out_port != datapath.ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst_mac, eth_src=src_mac)
            inst = [parser.OFPInstructionActions(datapath.ofproto.OFPIT_APPLY_ACTIONS, actions)]
            mod = parser.OFPFlowMod(datapath=datapath, priority=10, match=match,
                                    instructions=inst, idle_timeout=15)
            datapath.send_msg(mod)

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=msg.data)
        datapath.send_msg(out)
