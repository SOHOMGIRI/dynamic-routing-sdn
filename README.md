# Dynamic Routing Optimization in Software-Defined Networking (SDN)
### Adaptive Path-Finding for Data Packets in Constantly Changing Network Topologies

**Department of Computer Science & Engineering**  
**St. Thomas' College of Engineering & Technology, Kolkata**  
*(Affiliated to Maulana Abul Kalam Azad University of Technology - MAKAUT)*

---

## 👥 Project Team & Contributions

| Member Name | University Roll Number | Primary Responsibilities & Git Feature Branch |
| :--- | :--- | :--- |
| **Sohom Giri** *(Lead)* | `12200123157` | **Core Adaptive Routing Engine:** OpenFlow 1.3 Ryu Controller, Dynamic Non-Linear Cost Algorithm, Elephant Flow Detouring & Sub-15ms Failover (`feature/adaptive-routing-engine`) |
| **Bratin Roy** | `12200123042` | **Network Infrastructure, Traffic Synthesis & Chaos:** Mininet Multi-path Mesh Topology, iperf3 Elephant/Mice Traffic Generator & Link Chaos Injector (`feature/network-topology-and-chaos`) |
| **Bisal Mondal** | `12200123039` | **Telemetry & Live UI Dashboard:** Real-Time Telemetry Pipeline, Interactive Streamlit Web Monitoring Dashboard & Benchmark Visualizations (`feature/telemetry-and-dashboard`) |

**Project Supervisor:** Dr. Sanghamitra De (Department of CSE, STCET)

---

## 📌 Problem Statement & Real-World Motivation

Modern enterprise and cloud networks suffer from two critical routing limitations:
1. **Elephant vs. Mice Flow Bottlenecks:** Traditional shortest-path algorithms (OSPF, ECMP) forward packets blindly along the shortest hop-count path. When massive data transfers ("elephant flows") collide on a bottleneck link, queue buffers overflow, causing packet loss and latency spikes for critical, small "mice flows".
2. **High Link Churn & Micro-loops:** Dynamic environments (disaster response mesh networks, data center fabric failures) cause link severance. Traditional link-state re-flooding takes seconds to converge, dropping thousands of inflight packets.

### Our Solution
A **Hybrid Software-Defined Networking (SDN) Adaptive Controller** that decouples packet forwarding from routing intelligence:
* **Mice Flows:** Continue along the pre-computed hardware-speed shortest path (Dijkstra SPF).
* **Elephant Flows & Congestion Mitigation:** The controller polls OpenFlow switch port statistics periodically. When link utilization exceeds a dynamic threshold ($\tau = 70\%$), the controller calculates a latency-optimized alternative detour path and dynamically pushes OpenFlow `FlowMod` rules to reroute traffic before buffer overflow occurs.
* **Instant Failover:** Automatic path re-computation upon link-down events without global link-state broadcast floods.

---

## 🏗️ System Architecture

```text
       ┌─────────────────────────────────────────────────────────────┐
       │             Ryu SDN Controller (Control Plane)              │
       │                                                             │
       │  ┌───────────────────────┐       ┌───────────────────────┐  │
       │  │   Telemetry Engine    │       │  Adaptive Dynamic     │  │
       │  │  (Port Stats Polling) │──────▶│  Path-Finding Engine  │  │
       │  └───────────────────────┘       └───────────┬───────────┘  │
       └──────────────────────────────────────────────┼──────────────┘
                          ▲ OpenFlow 1.3              │ FlowMod Rules
                          │ Port Stats (every 1s)     │ (Pushed to switches)
       ┌──────────────────┼───────────────────────────▼──────────────┐
       │                  │    Mininet Data Plane                    │
       │                                                             │
       │      [Host 1] ─── (Switch 1) ════════ (Switch 2) ─── [Host 2]
       │                        │                     │              │
       │                        └─── (Switch 3) ──────┘              │
       │                                                             │
       │           ════ Congested direct link                        │
       │           ──── Dynamically calculated low-load detour       │
       └─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
       ┌─────────────────────────────────────────────────────────────┐
       │              Interactive Streamlit Web Dashboard            │
       │  - Live Topology View          - Throughput & Bandwidth     │
       │  - Packet Loss % Tracker       - RTT Latency Comparison     │
       └─────────────────────────────────────────────────────────────┘
```

---

## 📂 Repository Structure

```text
dynamic-routing-sdn/
├── README.md                  # Comprehensive technical documentation & setup
├── requirements.txt           # Python library dependencies
├── .gitignore                 # Files ignored by git (caches, logs, pcap)
│
├── topologies/                # [Sohom Giri] Mininet network creation scripts
│   ├── mesh_topology.py       # Custom 6-node redundant mesh topology
│   └── spine_leaf.py          # Data center 2-tier spine-leaf fabric
│
├── traffic_engine/            # [Sohom Giri] Traffic synthesis & chaos testing
│   ├── traffic_generator.py   # Automated iperf3 traffic matrix generator
│   └── chaos_injector.py      # Automated link failure & recovery script
│
├── controller/                # [Bisal Mondal] Ryu SDN Controller & Algorithms
│   ├── baseline_dijkstra.py   # Classical OSPF/Shortest Path baseline
│   └── adaptive_controller.py # Real-time congestion-aware dynamic routing
│
├── analytics/                 # [Bratin Roy] Telemetry & Live Web Dashboard
│   ├── telemetry_logger.py    # Logs RTT, packet loss, and throughput to CSV
│   └── dashboard.py           # Streamlit live monitoring web interface
│
└── scripts/                   # Helper automation scripts
    ├── run_simulation.sh      # 1-command startup script
    └── setup_wsl.sh           # Environment setup for Ubuntu/WSL2
```

---

## 🚀 Quickstart Guide

### Prerequisites
* Operating System: **Ubuntu 20.04 / 22.04 LTS** (or Windows 10/11 with **WSL2 Ubuntu**)
* Python 3.8 - 3.10
* Mininet & Open vSwitch
* Ryu SDN Controller

### 1. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/dynamic-routing-sdn.git
cd dynamic-routing-sdn

# Install Python requirements
pip install -r requirements.txt

# Install Mininet & Open vSwitch (Ubuntu/WSL2)
sudo apt update
sudo apt install -y mininet openvswitch-switch iperf3 tshark
```

### 2. Running the System
Open three separate terminal windows:

**Terminal 1 (Start Ryu SDN Controller):**
```bash
ryu-manager controller/adaptive_controller.py --observe-links
```

**Terminal 2 (Start Mininet Topology):**
```bash
sudo python3 topologies/mesh_topology.py
```

**Terminal 3 (Launch Live Monitoring Dashboard):**
```bash
streamlit run analytics/dashboard.py
```

---

## 📊 Evaluation Metrics
1. **Average Round-Trip Latency (ms)** under varying traffic loads.
2. **Packet Loss Ratio (%)** during sudden link severance.
3. **Failover Convergence Time (ms)** comparing Classical OSPF vs. Adaptive SDN.
4. **Link Utilization Balance (Jain's Fairness Index)** across alternate paths.
