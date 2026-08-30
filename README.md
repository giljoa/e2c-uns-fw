# A Unified Namespace-Based Edge-to-Cloud Framework for Industrial Data Analytics

**IEEE LATAM Submission ID: 10869**

**Authors:**
- Joaquín D. López¹ ([0009-0006-6132-0114](https://orcid.org/0009-0006-6132-0114))
- Juliam A. Díaz¹ ([0009-0000-7507-7692](https://orcid.org/0009-0000-7507-7692))
- Natalia Duarte² ([0009-0009-1319-1938](https://orcid.org/0009-0009-1319-1938))
- Iván Hernández² ([0009-0002-5037-8477](https://orcid.org/0009-0002-5037-8477))
- Carlos A. Fajardo¹ ([0000-0002-8995-4585](https://orcid.org/0000-0002-8995-4585))
- Juan M. Rey¹ ([0000-0002-5465-4769](https://orcid.org/0000-0002-5465-4769))

¹ Escuela de Ingenierías Eléctrica, Electrónica y de Telecomunicaciones (E3T), Universidad Industrial de Santander (UIS), Bucaramanga, Colombia
² [DAUTOM S.A.S.](https://www.dautom.com.co/), Bucaramanga, Colombia

---

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

## Repository Contents

A full description of every file and directory a user needs to run or reproduce the framework:

| Path | Description |
|---|---|
| `arch-components/Publisher.py` | Edge script. Replays a dataset's CSV files over MQTT, simulating one or more edge devices publishing high-frequency vibration (or temperature) data. |
| `arch-components/Diagnosis.py` | Cloud script. Subscribes to raw vibration vectors, performs Hilbert-transform + FFT feature extraction, runs CNN inference, and publishes fault predictions (and temperature-threshold alarms) back to the UNS. |
| `requirements.txt` | Python dependencies for both `Publisher.py` and `Diagnosis.py`, and for `ml/data-prep/tdms_to_csv.py`. |
| `flex-tig-stack/docker-compose.yml` | Deploys the historian/visualization stack: Telegraf, InfluxDB, and Grafana. |
| `flex-tig-stack/telegraf/telegraf.conf` | Maps each UNS MQTT topic to an InfluxDB measurement (one `mqtt_consumer` input block per topic). |
| `flex-tig-stack/grafana/*.json` | Grafana dashboard exports (Overview, Device View, Temperature Device View, MotorDB) — see [Getting Started](#getting-started) for how to import them; they are not auto-provisioned. |
| `ml/data-prep/data.ipynb` | Loads the raw KAIST/CWRU `.mat` files, resamples CWRU to match KAIST's 25.6 kHz, and builds the train/val/test manifests consumed by the training notebooks. |
| `ml/data-prep/tdms_to_csv.py` | Converts the KAIST temperature dataset's `.tdms` files to the CSV format `Publisher.py` streams from. |
| `ml/model-nb/CNN_Generalizability.ipynb`, `CNN_Usman2024.ipynb` | Model training and evaluation notebooks — cross-dataset transfer learning between KAIST and CWRU, producing the CNN used by `Diagnosis.py`. |
| `ml/model-nb/module_plot.py` | Shared plotting helpers imported by the training notebooks. |
| `ml/models_transfer_backup/kaist_to_cwru_transfer.keras` | The trained 1D CNN model used for inference (the artifact `Diagnosis.py` loads). |
| `ml/models_transfer_backup/{kaist,cwru}_test_final/` | Evaluation reports and confusion matrices for the trained model on each dataset. |
| `experiments/Results1`–`Results4` | Raw data from the scalability experiments reported in the paper: per-device publish logs, per-host CPU/RAM logs, TIG-stack resource usage, and the cloud diagnosis service's console log, across a 3-device and a 9-device physically-independent-hardware deployment. |
| `experiments/monitor_publisher.py` | Cross-platform (Linux/Windows) CPU/RAM logger used to collect the per-host resource logs in `experiments/`. |
| `CLAUDE.md` | Detailed architecture and data-flow reference (UNS topic list, data layout, notebook pipeline) — the most complete single reference beyond this README. |

---

## Reproducing the Paper's Results

- **Scalability** (Section VI-A): the raw data is in `experiments/Results1`–`Results4`; the code that generated it is `arch-components/Publisher.py` (edge simulation, run across multiple physically independent hosts) and `arch-components/Diagnosis.py` (the single-threaded cloud inference stage whose capacity limit the results characterize).
- **Generalizability**: `ml/model-nb/CNN_Generalizability.ipynb` and `CNN_Usman2024.ipynb` train and evaluate the cross-dataset transfer-learning model; `ml/models_transfer_backup/` holds the resulting trained model and its evaluation reports/confusion matrices.
- **Accessibility**: `flex-tig-stack/` is the complete open-source deployment (Telegraf, InfluxDB, Grafana) referenced in the accessibility measurements — hardware/software footprint, container sizes, and deployment steps are as described in [Getting Started](#getting-started) below.

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

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/giljoa/e2c-uns-fw.git
   cd e2c-uns-fw
   pip install -r requirements.txt
   ```
2. Supply the publisher data. `data/publish-data/<dataset>/` (one CSV per class label) is required by `Publisher.py` but is **not included in this repository** — it's local-only, gitignored data. If you don't already have it, contact the authors for a copy; there is no way to regenerate it from what's checked in here (the raw vendor `.mat`/`.tdms` files it's derived from are gitignored too).
3. Deploy the TIG stack (Telegraf, InfluxDB, Grafana):
   ```bash
   cd flex-tig-stack
   docker compose up -d
   ```
   Then import the dashboards under `flex-tig-stack/grafana/*.json` into Grafana manually (Dashboards → Import) — they are exports, not auto-provisioned by `docker-compose.yml`.
4. Run the publisher simulation:
   ```bash
   python arch-components/Publisher.py --device Motor1 --dataset kaist
   ```
5. Start the diagnosis service. `Diagnosis.py` loads its model from a hard-coded Google Colab Drive path by default (it was written to run inside Colab) — edit the `model = keras.models.load_model(...)` line to point at `ml/models_transfer_backup/kaist_to_cwru_transfer.keras` before running it locally:
   ```bash
   python arch-components/Diagnosis.py
   ```

See `CLAUDE.md` for the full UNS topic reference, data layout, and additional troubleshooting notes.

## Citation

If you use this repository in academic work, please cite:

- Gilbert Delgado. An IIoT Cloud Based Solution for Fault Diagnosis of Induction Motors. MSc Thesis, Universidad Industrial de Santander, 2025.
- Joaquín D. López et al. "A Unified Namespace-Based Edge-to-Cloud Framework for Industrial Data Analytics." (Submitted for publication).
