#!/bin/bash
# Script to launch Sohom Giri's Adaptive SDN Controller
echo "====================================================="
echo "   STARTING RYU ADAPTIVE CONTROLLER (Sohom Giri)     "
echo "====================================================="
ryu-manager --ofp-tcp-listen-port 6653 controller/adaptive_controller.py --observe-links
