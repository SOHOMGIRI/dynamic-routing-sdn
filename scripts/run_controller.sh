#!/bin/bash
# Script to launch Sohom Giri's Adaptive SDN Controller
echo "====================================================="
echo "   STARTING RYU ADAPTIVE CONTROLLER (Sohom Giri)     "
echo "====================================================="
ryu-manager controller/adaptive_controller.py --observe-links
