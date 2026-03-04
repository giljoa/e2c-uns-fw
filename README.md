# A Unified Namespace-Based Edge-to-Cloud Framework for Industrial Data Analytics

## Overview  
This repository provides the implementation of a **Unified Namespace (UNS)-based architectural formalization** designed for scalable and interoperable industrial analytics. While the framework is validated through an **induction motor (IM) fault diagnosis** case study, its primary contribution is a technology-agnostic backbone that bridges the gap between isolated edge devices and enterprise-level IT services.

The implementation is built upon three core design pillars:
- **Scalability**: Demonstrated through a decoupled publish-subscribe model that maintains low-latency performance under increasing data loads.
- **Generalizability**: Validated via cross-dataset transfer learning (KAIST and CWRU datasets) without requiring architectural reconfiguration.
- **Accessibility**: Optimized for deployment using open-source tools and free-tier infrastructure, lowering the barrier for industrial adoption.

---

## Architecture  

The framework follows a formal **five-component data flow** structured within a Unified Namespace:

1.  **Edge Layer**: High-frequency data acquisition (25.6 kHz) with window-based batching to optimize MQTT throughput.
2.  **Unified Namespace (UNS)**: An event-driven integration layer that enforces a semantic hierarchy based on **ISA-95 functional levels**.
3.  **Data Cloud**: A centralized processing hub for feature extraction (Hilbert + FFT) and CNN-based inference.
4.  **Historian**: Persistent time-series storage using InfluxDB for both raw signals and diagnostic metadata.
5.  **Client Layer**: Near-real-time visualization via Grafana dashboards, providing end-to-end visibility.

---

## Technical Specifications

### High-Frequency Data Handling
To handle the demanding requirements of vibration-based fault diagnosis, the edge component manages:
- **Sampling Rate**: 25.6 kHz high-fidelity vibration signals.
- **Batching Strategy**: Because standard protocols are not optimized for individual message transmission at 25.6 kHz, the system implements a **window-based batching strategy**. This groups samples into discrete packets to maintain semantic coherence while keeping operational latency **below one second**.

### Semantic Mapping
The UNS utilizes a hierarchical topic structure that mirrors the physical and logical organization of industrial assets:
`Enterprise / Site / Area / Line / Cell / Device / Tag`

This structure enables the seamless integration of hybrid systems like **Manufacturing Execution Systems (MES)**, allowing them to synchronize high-level work orders with real-time shop-floor insights.

---

## Key Components  

- **Publisher (`Publisher.py`)**: Simulates edge nodes by replaying high-frequency vibration signatures from the KAIST and CWRU datasets.
- **Diagnosis (`Diagnosis.py`)**: A subscriber-based service that performs Hilbert transforms and FFT-based feature extraction followed by CNN classification.
- **Model (`ml/models/multi_domain_model_fold_1.h5`)**: A 1D Convolutional Neural Network (CNN) optimized for cross-domain generalizability.
- **TIG Stack (`docker-compose.yaml`)**: Orchestrates **Telegraf, InfluxDB, and Grafana** for a robust, open-source historian and visualization layer.

---

## Results & Validation

The framework has been rigorously tested to confirm the three pillars:
- **Performance**: Sustained mean end-to-end latencies **< 1.0s** for concurrent edge devices sampling at **25.6 kHz**.
- **Accuracy**: Diagnostic accuracy exceeding **98%** in cross-dataset scenarios (transferring knowledge between KAIST and CWRU domains).
- **Interoperability**: Successful convergence of OT-level data with IT-level analytics platforms without architectural silos.

---

## Future Work
- **Advanced Scalability**: Testing the framework under extreme loads using higher hardware specifications.
- **Protocol Expansion**: Incorporating additional industrially adopted data protocols to enhance generalizability across diverse assets.
- **Security & Governance**: Implementation of granular access control and encryption at the broker level.

---

## Getting Started  

1. Clone the repository: 
   ```bash
   git clone https://github.com/giljoa/e2c-uns-fw.git
   cd <your-repo-location>
   ```
2. Deploy TIG stack
   ```bash
   docker-compose -f \flex-tig-stack\docker-compose.yml up -d
   ```
4. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
5. Run the publisher simulation:
   ```bash
   python Publisher.py --device Motor1
   ```
6. Start the diagnosis service:
   ```bash
   python Diagnosis.py --device Motor1
   ```

## Citation

If you use this repository in academic work, please cite:

- Gilbert Delgado. An IIoT Cloud Based Solution for Fault Diagnosis of Induction Motors. MSc Thesis, Universidad Industrial de Santander, 2025.
- Joaquín D. López et al. "A Unified Namespace-Based Edge-to-Cloud Framework for Industrial Data Analytics." (Submitted for publication).
