# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A Unified Namespace (UNS)-based IIoT framework for induction-motor fault diagnosis, built around three pillars: **scalability** (MQTT-based edge publisher/diagnosis services that scale horizontally per device), **generalizability** (a CNN trained across the KAIST and CWRU datasets via transfer learning), and **accessibility** (open-source stack only: Python, MQTT, InfluxDB, Grafana, Colab).

This is a research/thesis codebase (companion to a submitted IEEE Latam Transactions article), not a product with CI — there is no test suite, linter config, or build system. Treat notebooks under `ml/` as the source of truth for data-prep and model-training logic; the `.py` files under `arch-components/` are the runtime services.

## Commands

```bash
pip install -r requirements.txt

# Edge publisher — simulates a device streaming a dataset's CSVs over MQTT
python arch-components/Publisher.py --device Motor1 --dataset kaist   # or --dataset cwru

# Cloud diagnosis service — subscribes to raw vectors, runs CNN inference, publishes predictions
python arch-components/Diagnosis.py

# TIG stack (Telegraf + InfluxDB + Grafana), from flex-tig-stack/
docker-compose up -d
```

`Diagnosis.py` loads its Keras model from a hard-coded Google Drive path (`/content/drive/MyDrive/FlexUNS/...`), i.e. it's written to run inside Google Colab, not locally — update `model = keras.models.load_model(...)` to a local path before running it outside Colab.

There are no automated tests, lint rules, or CI in this repo currently.

## Architecture

### Edge-to-cloud data flow (the UNS pipeline)

```
Publisher.py  --MQTT-->  HiveMQ broker  --MQTT-->  Telegraf  -->  InfluxDB  -->  Grafana
                              |
                              +--MQTT-->  Diagnosis.py --MQTT--> (predictions back to broker/Telegraf)
```

All MQTT topics follow a fixed UNS hierarchy rooted at `Enterprise/Site/Area/{DEVICE_ID}/...`:

- `.../Edge/MotorModel/vibration` — downsampled raw signal for storage (Publisher → Telegraf → InfluxDB `vibration_data`)
- `.../Analysis/Vibration/raw_vector` — full-rate signal for compute (Publisher → Diagnosis.py)
- `.../Analysis/Vibration/fft` — FFT spectrum computed by Diagnosis.py (→ InfluxDB `fft_vibration`)
- `.../Analysis/Diagnosis/prediction` — CNN fault prediction (→ InfluxDB `fault_diagnosis`)
- `.../Metrics/vibration_publisher/*`, `.../Metrics/cloud_diagnosis` — payload-size/latency telemetry (→ InfluxDB `payload_metrics`)

Both `Publisher.py` and `Diagnosis.py` independently sync to an NTP server (`pool.ntp.org`) to timestamp payloads in nanoseconds, since edge/cloud clock drift is used to measure end-to-end latency (`raw_latency_ms` in `Diagnosis.py`). MQTT broker choice and credentials are selected via a `var` int flag (0/1/2) near the top of each script — currently all point at a shared HiveMQ Cloud instance hard-coded in the source.

`telegraf.conf` (`flex-tig-stack/telegraf/`) has one `[[inputs.mqtt_consumer]]` block per topic above, each mapping a topic to an InfluxDB measurement via `name_override`. `downsample.star` is an optional (currently commented-out) Starlark processor for further downsampling in Telegraf itself.

### Data layout (`data/`, gitignored — all data is local-only, never committed)

- `data/raw_<dataset>/` — original vendor files (`.mat` for CWRU/KAIST vibration, `.tdms`/`.tdms_index` for KAIST current+temperature, National Instruments format).
- `data/flex-data/<dataset>_csv/vibration<rate>_domain<load>/` — per-domain CSV cache produced by `ml/data-prep/data.ipynb`, consumed by the training notebooks so raw `.mat` files aren't re-parsed every run.
- `data/publish-data/<dataset>/*.csv` — one CSV per class label (e.g. `0Nm_BPFI_03.csv`), headerless-style numeric columns (KAIST vibration = 4 channels, CWRU = 2–3 channels). This is the folder `Publisher.py --dataset <dataset>` streams from; it picks a random file each loop and republishes it 3x. Column count is validated in `Publisher.py` per dataset, so new data sources need either a matching column count or an update to that validation branch.
- `ml/models_transfer_backup/` — backup copies of trained model artifacts + evaluation reports/confusion matrices for CWRU/KAIST transfer tests. `ml/models/` (the path `Diagnosis.py` ultimately loads from, via Drive) is gitignored and not present in the repo checkout.

### ML notebooks (`ml/`)

- `ml/data-prep/data.ipynb` — loads raw `.mat` files per dataset/domain, caches to CSV under `flex-data/`, resamples CWRU (12 kHz) to match KAIST's 25.6 kHz, and builds `manifest.csv` / train / val / test split CSVs used by the model notebooks.
- `ml/model-nb/CNN_Generalizability.ipynb`, `CNN_Usman2024.ipynb` — model training/evaluation notebooks (transfer learning across KAIST/CWRU domains); `module_plot.py` holds shared plotting helpers imported by these notebooks.

### Grafana (`grafana/*.json`)

Dashboard exports (`Overview.json`, `Device View.json`, `MotorDB.json`) meant to be imported manually into Grafana — they are not auto-provisioned by `docker-compose.yml`.
