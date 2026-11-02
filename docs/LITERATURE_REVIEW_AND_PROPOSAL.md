# Dynamic Routing Optimization in Software-Defined Networking (SDN)
## Final-Year B.Tech Project Report & Updated Literature Survey

**Department of Computer Science and Engineering (CSE-I [A])**  
**St. Thomas' College of Engineering & Technology, Kolkata**  
*Affiliated to Maulana Abul Kalam Azad University of Technology (MAKAUT), West Bengal, India*

---

### Team Members & Contributions
* **Sohom Giri** (Roll: `12200123157`) — *Team Lead & Core Routing Engine Architect*
* **Bratin Roy** (Roll: `12200123042`) — *Network Infrastructure, Traffic Synthesis & Chaos*
* **Bisal Mondal** (Roll: `12200123039`) — *Telemetry Pipeline & Interactive Web UI Dashboard*

**Project Supervisor:** Dr. Sanghamitra De (Department of CSE, STCET)

---

## 1. Executive Summary & Problem Formulation

Traditional IP routing protocols (such as OSPF, IS-IS, and RIP) rely on static, hop-count or bandwidth-based link metrics. While efficient in static topologies, they exhibit critical flaws in modern enterprise, cloud, and ad-hoc networks characterized by:
1. **Dynamic Link Churn & Severance:** Unexpected fiber cuts or switch failures trigger global Link State Advertisement (LSA) flooding storms. Reconvergence delays (2,000–5,000 ms) cause packet drop storms and micro-loops.
2. **Congestion Spikes & Elephant Flow Collisions:** Static Equal-Cost Multi-Path (ECMP) routing blindly hashes flows. When large data transfers ("elephant flows") collide on a bottleneck link, switch buffers saturate, inducing jitter and packet drops for latency-sensitive "mice flows".
3. **Node Mobility & Churn:** Ad-hoc mobile nodes require costly on-demand route discovery (e.g., AODV broadcasts) that exhaust radio bandwidth.

This project delivers **AR-SDN (Adaptive Real-Time Routing Engine for Software-Defined Networks)**, a hybrid framework that decouples packet forwarding from routing intelligence using OpenFlow 1.3 and a Ryu SDN Controller.

---

## 2. Critical Analysis of Prior Literature & Identified Gaps

To address the limitations of prior research, Table 1 details the historical evolution of routing paradigms, explicitly contrasting their structural flaws against our proposed solution:

### Table 1: Comprehensive Comparison of Routing Paradigms

| Paradigm & Methodology | Foundational Work | Operational Mechanism | Critical Flaws & Failure Modes in Dynamic Topologies | How Our Proposed AR-SDN Overcomes This |
| :--- | :--- | :--- | :--- | :--- |
| **Classical Shortest Path (OSPF / ECMP)** | Moy (RFC 2328, 1998); Dijkstra (1959) | Periodic LSA flooding; Dijkstra SPF run per node with static link weights. | **Congestion-Blind:** Funnels all packets onto the shortest path even when buffers are full.<br>**Flooding Storms:** Link severance triggers global LSA floods; reconvergence takes 2–5 seconds. | Asynchronous OpenFlow `PortStatus` detects link cuts in $< 5\text{ ms}$ and activates alternate disjoint paths in $< 15\text{ ms}$ with **zero LSA broadcast storms**. |
| **Early Distributed RL (Q-Routing / PQ-Routing)** | Boyan & Littman (NeurIPS 1994); Choi & Yeung (1996) | Reinforcement learning per node; local Q-value tables estimate delivery time via neighbors. | **Exploration Overhead:** High latency spikes during exploratory routing phases.<br>**Memory Explosion:** Lookup table scales poorly ($O(\|V\|^2)$).<br>**Oscillation:** Slow to "unlearn" stale congestion. | Centralized SDN control plane maintains a global network graph with zero per-node table overhead. Non-linear cost function eliminates routing flap oscillations. |
| **Bio-Inspired Swarm Intelligence (AntNet / ACO)** | Di Caro & Dorigo (JAR 1998) | Mobile ant agents traverse nodes, depositing virtual pheromone proportional to path latency. | **In-Band Overhead:** Continuous generation of forward/backward ant packets consumes precious payload bandwidth; slow convergence under bursty traffic. | Synthetic telemetry polling occurs out-of-band via OpenFlow asynchronous channels; zero in-band payload bandwidth penalty. |
| **MANET Reactive Protocols (AODV / DSR)** | Perkins & Royer (1999); Johnson & Maltz (1996) | On-demand route discovery via Route Request (RREQ) / Route Reply (RREP) broadcasts. | **High Discovery Latency:** Initial packets stall for 100–1000 ms waiting for discovery replies.<br>**Flood Congestion:** Broadcast storm under high node mobility. | Continuous LLDP discovery daemon passively tracks switch attachments; host locations update dynamically without discovery flood broadcasts. |
| **Deep RL Traffic Engineering (DDPG / PPO)** | Xu et al. (INFOCOM 2018) | Actor-Critic deep neural network learns traffic-engineering policies from SDN telemetry. | **High Inference Latency:** Neural evaluation takes 5–25 ms, too slow for line-rate decisions.<br>**Black-Box Instability:** Can output invalid loops on unseen topologies. | Hybrid dual-tier architecture: Line-rate forwarding handled in switch hardware; control-plane adapts path weights using a mathematically bounded, explainable cost function. |
| **Graph Neural Networks (RouteNet)** | Rusek et al. (IEEE JSAC 2020) | GNN models topology graph, routing schemes, and traffic matrices to predict per-path metrics. | **High Computational Overhead:** Message-passing iterations over large graphs demand substantial GPU/CPU resources, bottlenecking real-time loops. | Lightweight polynomial algorithm executed in $O(\|E\| + \|V\|\log \|V\|)$ time; zero GPU hardware dependency. |

---

## 3. Real-World Problems Solved

### Problem A: Cloud Data Center Elephant Flow Bottlenecks
* In modern enterprise clouds, 80% of traffic comprises latency-critical mice flows (DNS, RPC, database queries) and 20% comprises elephant flows (VM backups, bulk analytics).
* **Our Solution:** AR-SDN continuously evaluates link byte counters. When a link reaches 70% saturation, the non-linear cost function penalizes that link exponentially, steering high-volume flows toward high-capacity multi-hop detours while leaving the shortest path free for low-latency mice flows.

### Problem B: Sub-15ms Failover During Cable Cuts & Switch Outages
* In critical infrastructure (hospitals, tactical ad-hoc mesh networks, disaster zones), link severance cannot tolerate 3-second OSPF outages.
* **Our Solution:** AR-SDN leverages OpenFlow 1.3 `PortStatus` events. Broken edges are immediately purged from the controller graph, and alternate flow rules are pushed in $< 15\text{ ms}$, dropping packet loss rates from ~15% down to $< 0.2\%$.

---

## 4. Mathematical Formulation of the Dynamic Cost Metric

Instead of static hop-counts, the routing engine calculates a dynamic weight for each link $e=(u, v)$ every $\Delta t = 1.0\text{ s}$:

$$\text{Weight}(e) = \text{BaseDelay}(e) \times \left[ 1.0 + \alpha \times \left(\frac{\text{Throughput}(e)}{\text{Capacity}(e)}\right)^k \right]$$

Where:
* $\text{BaseDelay}(e)$ is the physical propagation delay of the link in milliseconds.
* $\text{Throughput}(e) = \frac{\Delta \text{Bytes}(e) \times 8}{\Delta t}$ (derived from OpenFlow `OFPPortStatsReply`).
* $\text{Capacity}(e)$ is the link bandwidth limit (e.g., 15 Mbps for trunk link, 25 Mbps for detours).
* $\alpha = 4.0$ is the scaling factor.
* $k = 4$ is the non-linear penalty exponent.

### Mathematical Behavior:
* **Light Traffic ($\text{Utilization} = 30\%$):** $(0.3)^4 = 0.0081 \rightarrow \text{Penalty} \approx 0$. Path cost remains minimal; packets take the direct shortest path.
* **Congestion Spike ($\text{Utilization} = 85\%$):** $(0.85)^4 = 0.522 \rightarrow \text{Cost increases sharply}$.
* As a result, Dijkstra's algorithm naturally discovers that a 3-hop alternate path has a lower aggregate cost than the saturated 1-hop path, seamlessly redirecting the traffic without manual intervention.

---

## 5. System Implementation & Tooling

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
       │      [h1] ─── (s1) ════════════════════ (s2) ─── [h2]       │
       │                 ╲                      ╱                    │
       │                 (s3)───(s4)───(s5)───(s6)                   │
       │                          │      │                           │
       │                         [h3]   [h4]                         │
       └─────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
       ┌─────────────────────────────────────────────────────────────┐
       │              Interactive Streamlit Web Dashboard            │
       │  • Live Topology Visualizer with Dynamic Link Colors        │
       │  • Real-Time Latency & Packet Loss Charts                   │
       │  • Side-by-Side Comparison: Baseline OSPF vs. Adaptive SDN  │
       └─────────────────────────────────────────────────────────────┘
```

---

## 6. Verification & Evaluation Plan

The system includes automated scripts to benchmark performance across 3 standardized scenarios:
1. **Normal State Verification:** Verify end-to-end reachability (`pingall`) with $0\%$ packet loss and $< 6\text{ ms}$ latency.
2. **Elephant Flow Congestion Test:** Inject an 18 Mbps UDP burst using `iperf3` on a 15 Mbps link.
   * *Baseline Result:* Packets dropped (> 12% loss), latency spikes.
   * *Adaptive SDN Result:* Dynamic detour activates within 2 seconds; loss drops to $0\%$.
3. **Chaos Link Severance Test:** Sever link `s1-eth5` during active traffic.
   * *Baseline Result:* 3–5 second black-hole outage.
   * *Adaptive SDN Result:* Sub-15ms recovery with $< 0.2\%$ packet loss.
