# OBD Intelligence

Real-time vehicle diagnostics that stream OBD-II sensor data, detect likely faults with a trained model, and explain what the readings mean in plain language using a local LLM.

## Architecture

```
+------------------------+
|  Car (OBD-II port)     |
+-----------+------------+
            | CAN bus
            v
+------------------------+
|  ELM327 dongle         |
|  BLE / WiFi            |
+-----------+------------+
            | PID frames
            v
+------------------------+
|  python-OBD            |
|  stream PIDs (~1 Hz)   |
+-----------+------------+
            | samples
            v
+------------------------+
|  Feature extractor     |
|  5-min window:         |
|  mean, std, slope      |
+-----------+------------+
            | feature vector
            v
+------------------------+
|  XGBoost               |
|  -> fault probabilities|
+-----------+------------+
            | {misfire: 0.78}
            v
+------------------------+
|  Trigger               |
|  prob > threshold      |
|  OR user asks          |
+-----------+------------+
            | prompt
            v
+------------------------+
|  Gemma (llama.cpp)     |
|  -> explanation        |
+-----------+------------+
            | tokens
            v
+------------------------+
|  UI (Gradio / app)     |
+------------------------+
```

## How it works

1. **Data collection** -- An ELM327 adapter plugged into the car's OBD-II port reads live sensor values over the CAN bus. The adapter connects over BLE or WiFi.

2. **Streaming** -- [python-OBD](https://github.com/brendan-w/python-OBD) polls standard PIDs (e.g. RPM, coolant temp, fuel trim, MAF) at roughly 1 Hz and yields a continuous time series.

3. **Feature extraction** -- A rolling 5-minute window aggregates each PID into summary statistics: **mean**, **standard deviation**, and **slope** (trend over the window). These form the input feature vector for inference.

4. **Fault detection** -- An XGBoost classifier trained on labeled driving sessions outputs per-fault probabilities (e.g. `{misfire: 0.78, vacuum_leak: 0.12, ...}`).

5. **Explanation trigger** -- Gemma is invoked when a fault probability crosses a configurable threshold, or whenever the user asks a question in the UI.

6. **Local LLM** -- [Gemma](https://ai.google.dev/gemma) runs locally via [llama.cpp](https://github.com/ggerganov/llama.cpp), receiving the current PID snapshot, extracted features, and top fault scores. It returns a human-readable explanation of what the readings suggest and what to check next.

7. **UI** -- A Gradio (or similar) app shows live gauges, fault probabilities, and the LLM's explanation.

## Components

| Layer | Technology | Role |
|-------|------------|------|
| Hardware | ELM327 dongle (BLE / WiFi) | Bridge between OBD-II port and host |
| Ingestion | python-OBD | Decode PID frames into typed samples |
| Features | Custom extractor | 5-min rolling mean, std, slope per PID |
| Model | XGBoost | Multi-label fault probability estimation |
| LLM | Gemma + llama.cpp | On-device natural-language explanations |
| Frontend | Gradio | Live dashboard and chat-style Q&A |

## Requirements

- Python 3.12 (conda env **`small-hack-1`**)
- ELM327-compatible OBD-II adapter (Bluetooth or Wi-Fi) -- or [ELM327-emulator](https://github.com/Ircama/ELM327-emulator) for local dev
- Trained XGBoost model weights
- Gemma model file (GGUF) for llama.cpp
- Vehicle with a standard OBD-II port (1996+ in the US)

## Development: OBD emulator (no hardware)

Use [ELM327-emulator](https://github.com/Ircama/ELM327-emulator) to simulate a car + ELM327 dongle.

1. Download the latest release from [GitHub Releases](https://github.com/Ircama/ELM327-emulator/releases/latest) (`elm327-emulator.zip`).
2. Extract to a permanent folder, e.g. `C:\Tools\elm327-emulator\`.
3. Add that folder to your **PATH** (Settings > Environment Variables > Path > New).
4. Open a **new terminal**, then verify: `elm327-emulator --version`
5. Start the emulator:

```powershell
elm327-emulator -s car -n 35000
```

Leave this running. Connect Python to `socket://localhost:35000`.

### Connect your app to the emulator

| Variable | Value (emulator) |
|----------|------------------|
| `OBD_PORT` | `socket://localhost:35000` |

Set `check_voltage=False` when creating the python-OBD connection.

```powershell
conda activate small-hack-1
pip install -r requirements.txt
```

## OBD queries and emulator testing

Discover every query your connection supports (emulator must be running):

```powershell
conda activate small-hack-1
python obd_connection.py --discover
```

Against the **`car`** scenario (Toyota Auris Hybrid), python-OBD reports **86 supported commands**. A real vehicle will differ.

### Live sensor data (Mode 01) -- streaming / features

| Command | Description |
|---------|-------------|
| `RPM` | Engine RPM |
| `SPEED` | Vehicle speed |
| `COOLANT_TEMP` | Engine coolant temperature |
| `ENGINE_LOAD` | Calculated engine load |
| `MAF` | Mass air flow |
| `INTAKE_PRESSURE` | Intake manifold pressure |
| `INTAKE_TEMP` | Intake air temperature |
| `SHORT_FUEL_TRIM_1` | Short-term fuel trim bank 1 |
| `LONG_FUEL_TRIM_1` | Long-term fuel trim bank 1 |
| `THROTTLE_POS` | Throttle position |
| `THROTTLE_POS_B` | Absolute throttle position B |
| `RELATIVE_THROTTLE_POS` | Relative throttle position |
| `THROTTLE_ACTUATOR` | Commanded throttle actuator |
| `TIMING_ADVANCE` | Ignition timing advance |
| `ABSOLUTE_LOAD` | Absolute load value |
| `BAROMETRIC_PRESSURE` | Barometric pressure |
| `COMMANDED_EGR` | Commanded EGR |
| `COMMANDED_EQUIV_RATIO` | Commanded equivalence ratio |
| `CONTROL_MODULE_VOLTAGE` | Control module voltage |
| `EVAPORATIVE_PURGE` | Commanded evaporative purge |
| `FUEL_STATUS` | Fuel system status |
| `HYBRID_BATTERY_REMAINING` | Hybrid battery remaining life |
| `O2_B1S2` | O2 bank 1 sensor 2 voltage |
| `O2_S1_WR_VOLTAGE` | Wide-range O2 sensor 1 voltage |
| `O2_S1_WR_CURRENT` | Wide-range O2 sensor 1 current |
| `O2_SENSORS` | O2 sensors present |
| `CATALYST_TEMP_B1S1` | Catalyst temp bank 1 sensor 1 |
| `CATALYST_TEMP_B1S2` | Catalyst temp bank 1 sensor 2 |
| `RUN_TIME` | Engine run time since start |

Emulator `CMD>` hex probes: `test 010c` (RPM), `test 010d` (SPEED), `test 0105` (COOLANT_TEMP), `test 0104` (ENGINE_LOAD), `test 0110` (MAF).

Python: `connection.query(obd.commands.RPM)` (replace `RPM` with any command above).

### Diagnostic / status commands (Mode 03 / 07)

| Command | Description |
|---------|-------------|
| `GET_DTC` | Stored trouble codes |
| `GET_CURRENT_DTC` | DTCs from current/last cycle |
| `CLEAR_DTC` | Clear DTCs and freeze data |
| `STATUS` | Status since DTCs cleared |
| `DISTANCE_W_MIL` | Distance with MIL on |
| `RUN_TIME_MIL` | Time with MIL on |
| `TIME_SINCE_DTC_CLEARED` | Time since codes cleared |
| `DISTANCE_SINCE_DTC_CLEAR` | Distance since codes cleared |
| `WARMUPS_SINCE_DTC_CLEAR` | Warm-ups since codes cleared |

### Freeze-frame snapshots (`DTC_*`)

42 commands in the `car` scenario, including `DTC_RPM`, `DTC_SPEED`, `DTC_COOLANT_TEMP`, `DTC_ENGINE_LOAD`, `DTC_MAF`, `DTC_INTAKE_PRESSURE`, `DTC_INTAKE_TEMP`, `DTC_SHORT_FUEL_TRIM_1`, `DTC_LONG_FUEL_TRIM_1`, `DTC_THROTTLE_POS`, `DTC_STATUS`, `DTC_FUEL_STATUS`, and related `DTC_*` variants.

### Capability discovery

| Command | Description |
|---------|-------------|
| `PIDS_A`, `PIDS_B`, `PIDS_C`, `PIDS_9A` | Which Mode 01 PIDs the ECU supports |
| `MIDS_A` | Which Mode 06 monitor IDs are supported |
| `OBD_COMPLIANCE` | OBD standard compliance |
| `FUEL_TYPE` | Fuel type |

### Adapter queries

| Command | Description |
|---------|-------------|
| `ELM_VERSION` | ELM327 firmware version string |
| `ELM_VOLTAGE` | Adapter voltage reading |

### Testing use cases

| # | Goal | How |
|---|------|-----|
| 1 | Smoke test connection | Terminal 1: `elm327-emulator -s car -n 35000`. Terminal 2: `python obd_connection.py` |
| 2 | List all supported queries + sample values | `python obd_connection.py --discover` |
| 3 | Probe a single PID in the emulator | At `CMD>`: `test 010c` (RPM), `test 010d` (speed) |
| 4 | Stream ~1 Hz for feature window dev | Run `obd_connection.py` or lower `WINDOW_MINUTES` |
| 5 | Simulate ignition off | At `CMD>`: `scenario engineoff` |
| 6 | Simulate ignition on | At `CMD>`: `scenario car` |
| 7 | Override a sensor value | At `CMD>`: set `emulator.answer['RPM']` then query from Python |
| 8 | Force sensor dropout | At `CMD>`: `emulator.answer['SPEED'] = '<writeln>NO DATA</writeln>'` |
| 9 | Read trouble codes | Query `GET_DTC` via `--discover` or python-OBD |
| 10 | Check which PIDs car supports | Query `PIDS_A`, `PIDS_B`, `PIDS_C` |
| 11 | Count emulator traffic | At `CMD>`: `counters` |
| 12 | Reset emulator state | At `CMD>`: `reset` |

## Quick start

**Terminal 1** -- start the emulator:

```powershell
elm327-emulator -s car -n 35000
```

**Terminal 2** -- run sample connection:

```powershell
conda activate small-hack-1
pip install -r requirements.txt
python obd_connection.py
python obd_connection.py --discover
```

When the full app exists:

```powershell
set OBD_PORT=socket://localhost:35000
python app.py
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OBD_PORT` | auto-detect | Serial / BLE address, or `socket://localhost:35000` for the emulator |
| `POLL_INTERVAL` | `1.0` | Seconds between PID reads |
| `WINDOW_MINUTES` | `5` | Rolling feature window length |
| `FAULT_THRESHOLD` | `0.6` | Min probability to auto-trigger LLM |
| `GEMMA_MODEL_PATH` | -- | Path to GGUF weights |
| `LLAMA_CPP_THREADS` | `4` | CPU threads for inference |

## Project layout

```
small-hack/
|-- obd_connection.py   # connect, stream, --discover supported queries
|-- app.py              # Gradio UI entry point (planned)
|-- obd/
|   |-- stream.py       # python-OBD polling loop
|   +-- pids.py         # PID definitions and decoding
|-- features/
|   +-- extractor.py    # Rolling window statistics
|-- model/
|   |-- train.py        # XGBoost training script
|   +-- infer.py        # Load model, score feature vectors
|-- llm/
|   +-- explain.py      # Gemma prompt + llama.cpp wrapper
+-- requirements.txt
```

## Disclaimer

This tool is for informational purposes only. It is not a substitute for professional diagnostics or repair. Always verify findings with a qualified mechanic before acting on them.