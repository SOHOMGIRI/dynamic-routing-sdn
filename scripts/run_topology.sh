#!/bin/bash
# Script to launch Bisal Mondal's Mininet Mesh Topology
echo "====================================================="
echo "   STARTING MININET MESH TOPOLOGY (Bisal Mondal)     "
echo "====================================================="
sudo mn -c
sudo python3 topologies/mesh_topology.py
