#!/bin/bash
# Script to cleanly stop all Mininet and Ryu background processes
echo "Cleaning Mininet, Open vSwitch and zombie controller processes..."
sudo mn -c
sudo killall ryu-manager 2>/dev/null || true
sudo killall iperf3 2>/dev/null || true
echo "Cleanup completed successfully."
