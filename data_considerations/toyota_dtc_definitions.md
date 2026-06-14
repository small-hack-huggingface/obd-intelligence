# Toyota DTC definitions

Diagnostic Trouble Code (DTC) reference for **Toyota** and **Toyota hybrid** vehicles (Auris Hybrid / Prius-class THS). Maps codes to the fault profiles used in this project.

For generic OBD modes and freeze-frame PIDs, see [pid_definitions.md](pid_definitions.md). For Toyota extended live PIDs, see [toyota_pid_definitions.md](toyota_pid_definitions.md).

---

## How DTCs work on OBD-II

A DTC is a 5-character code (e.g. `P0171`) stored when the ECU detects a fault that exceeds thresholds for a period of time.

| Mode | Command (python-OBD) | Returns |
|------|----------------------|---------|
| **03** | `GET_DTC` | **Confirmed** stored codes |
| **07** | `GET_CURRENT_DTC` | **Pending** codes (current/last cycle, not yet stored or cleared) |
| **04** | `CLEAR_DTC` | Clears codes and freeze-frame data |
| **02** | `DTC_*` PIDs | **Freeze frame** — PID snapshot when code set |

**MIL (check engine light):** Illuminates for most `P` codes that affect emissions. Some hybrid codes also trigger the **master warning** or **hybrid system** indicator on the dash — not always the same as MIL.

**Emulator note:** The `car` scenario returns **`GET_DTC: []`** by default. See [fault_simulation.md](fault_simulation.md) for optional DTC simulation.

---

## DTC format

```text
  P 0  1  7  1
  │ │  └──┴──┴─ SAE fault number (0–9999)
  │ └────────── Second digit: system category
  └──────────── First letter: domain
```

| Letter | Domain | Examples |
|--------|--------|----------|
| **P** | Powertrain (engine, transmission, hybrid) | `P0171`, `P0A80` |
| **B** | Body (A/C, airbags, locks) | `B1421` |
| **C** | Chassis (ABS, steering) | `C1234` |
| **U** | Network / communication | `U0100` |

### P-code second digit (powertrain)

| Digit | Meaning | Who defines fault list |
|-------|---------|------------------------|
| **0** | Generic (SAE standard) | SAE — same across brands |
| **1** | Manufacturer-specific | Toyota |
| **2** | Generic (SAE enhanced) | SAE |
| **3** | Manufacturer + SAE hybrid zone | Toyota hybrid (`P3xxx`) |

Toyota hybrids use many **`P0Axx`** (generic hybrid), **`P1xxx`** (Toyota-specific), and **`P3xxx`** (HV battery block) codes alongside normal **`P01xx`–`P04xx`** emissions codes.

---

## Code status (confirmed vs pending)

When reading Mode 03/07, each code may include a status nibble:

| Status | Meaning |
|--------|---------|
| Confirmed | Fault met storage criteria; MIL may be on |
| Pending | Detected this drive cycle; may clear or become stored |
| Permanent | Emissions-related; cannot clear until fault fixed and monitors complete |

For training labels, treat **confirmed + matching PID signature** as strongest ground truth. Pending codes are useful for early detection.

---

## DTCs from project fault profiles

Codes commonly associated with the 30 simulated faults in [fault_profiles.md](fault_profiles.md).

### Air and fuel

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0171** | System Too Lean (Bank 1) | Vacuum leak, weak fuel pump, dirty MAF, EVAP purge stuck open |
| **P0172** | System Too Rich (Bank 1) | Leaking injector |
| **P0174** | System Too Lean (Bank 2) | Same as P0171 on V6/dual-bank (N/A on 4-cyl Auris B1) |
| **P0101** | MAF Circuit Range/Performance | Dirty MAF |
| **P0106** | MAP Circuit Range/Performance | MAP sensor failure |
| **P0401** | EGR Insufficient Flow | Stuck closed EGR (P0402 = excessive flow / stuck open) |

### Ignition / misfire

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0300** | Random/Multiple Cylinder Misfire | Coil failure, dirty injectors, compression loss, head gasket |
| **P0301** | Cylinder 1 Misfire | Ignition coil cyl 1, injector stuck closed cyl 1 |
| **P0302** | Cylinder 2 Misfire | Same pattern |
| **P0303** | Cylinder 3 Misfire | Same pattern |
| **P0304** | Cylinder 4 Misfire | Same pattern |

Toyota often sets **P0300** before or with cylinder-specific codes under light misfire.

### Cooling

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0128** | Coolant Thermostat (coolant temp below regulating temp) | Thermostat stuck open |
| **P0217** | Engine Coolant Over Temperature | Thermostat stuck closed, fan failure, low coolant, head gasket |
| **P0117** | ECT Sensor Circuit Low | Coolant temp sensor failure (implausible cold) |
| **P0118** | ECT Sensor Circuit High | Coolant temp sensor short/high |

### Emissions / O2 / catalyst

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0420** | Catalyst System Efficiency Below Threshold (Bank 1) | Catalyst degradation or restriction |
| **P0430** | Catalyst Efficiency Below Threshold (Bank 2) | Dual-bank only |
| **P0136** | O2 Sensor Circuit (Bank 1 Sensor 2) | Downstream O2 drift/failure |
| **P0138** | O2 Sensor Circuit High Voltage (B1S2) | O2 stuck high |
| **P0441** | EVAP Incorrect Purge Flow | Purge valve stuck open |

### Sensors

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0112** | IAT Sensor Circuit Low | IAT stuck low / −40°C |
| **P0113** | IAT Sensor Circuit High | IAT stuck high |
| **P0122** | TPS Circuit Low | Throttle position sensor failure |
| **P0123** | TPS Circuit High | TPS failure |

### Electrical

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0562** | System Voltage Low | Alternator failure, weak battery |
| **P0563** | System Voltage High | Voltage regulator failure |

---

## Toyota hybrid DTCs (P0Axx and related)

Generic SAE hybrid codes used heavily on Toyota THS (Prius, Auris Hybrid, Corolla Hybrid, etc.).

### HV battery

| Code | Description | Typical cause |
|------|-------------|---------------|
| **P0A80** | Replace hybrid/EV battery pack | End-of-life pack, severe block imbalance |
| **P3011** | HV battery block 1 voltage imbalance | Weak block/module in block 1 |
| **P3012** | HV battery block 2 voltage imbalance | Weak block in block 2 |
| **P3013** | HV battery block 3 voltage imbalance | (pattern continues per block) |
| **P3014** | HV battery block 4 voltage imbalance | |
| **P0A7F** | Hybrid battery pack deterioration | Gradual capacity loss |
| **P0A92** | Hybrid battery temperature — high | Cooling fault, fan, blocked intake |
| **P0A93** | Inverter "A" cooling system performance | Inverter coolant pump/flow |
| **P0A94** | DC/DC converter performance | 12 V charging from HV system |

### Hybrid drive / inverter / MG

| Code | Description | Typical cause |
|------|-------------|---------------|
| **P0A0F** | Engine failed to start | Hybrid system cannot start ICE when requested |
| **P0A1F** | Drive motor "A" control module | MG2 inverter/controller |
| **P0A3F** | Generator position sensor circuit | MG1 resolver/sensor |
| **P0A78** | Drive motor "A" inverter performance | MG2 inverter overheating/fault |
| **P0A7A** | Generator inverter performance | MG1 inverter |
| **P0AFC** | Hybrid/EV battery system voltage | Pack voltage out of range |
| **P0AD9** | Hybrid battery positive contactor stuck closed | Main relay/contactor |
| **P0ADF** | Hybrid battery negative contactor stuck closed | Main relay/contactor |
| **P0C73** | Motor electronics coolant pump "A" | Inverter cooling pump |

### Hybrid system / readiness

| Code | Description | Notes |
|------|-------------|-------|
| **P0A81** | Hybrid battery pack cooling fan 1 control circuit | Battery fan relay/wiring |
| **P0A82** | Hybrid battery pack cooling fan 1 performance | Fan not moving enough air |
| **P3125** | Crankshaft position sensor signal | ICE start/sync in hybrid context |
| **P3190** | Engine does not start | Poor fuel, immobilizer, mechanical (hybrid display) |
| **P3191** | Engine does not start (insufficient RPM) | Starter, compression, fuel |

Exact subcodes vary by model year and region. Use Techstream or a Toyota-specific scanner for **infocode** detail (e.g. which block failed).

---

## Toyota manufacturer-specific (P1xxx) — selected

Toyota assigns **`P1xxx`** codes for powertrain functions not in the generic SAE list. Examples seen on Toyota hybrids and Atkinson engines:

| Code | Description |
|------|-------------|
| **P107A** | Fuel rail pressure sensor (some direct-injection engines) |
| **P108A** | Fuel pressure too low |
| **P1300** | Igniter circuit malfunction (specific cylinder — Toyota legacy) |
| **P1349** | VVTi system malfunction (variable valve timing) |
| **P1603** | Engine stall history |
| **P1604** | Startability malfunction |
| **P1605** | Rough idle |
| **P2122** | APP sensor circuit low (accelerator pedal) |
| **P2123** | APP sensor circuit high |

Always confirm against the **exact model year** service manual — P1 codes are not portable across Toyota platforms.

---

## Freeze frame (Mode 02)

When a DTC is stored, the ECU saves a snapshot of key PIDs. python-OBD exposes these as **`DTC_RPM`**, **`DTC_COOLANT_TEMP`**, **`DTC_SHORT_FUEL_TRIM_1`**, etc. — see [emulator_car_queries.md](emulator_car_queries.md).

| Use | Why it matters |
|-----|----------------|
| Validate simulation | Live fault PIDs should resemble freeze frame at code set |
| LLM explanation | “At the time P0171 set: STFT +22%, MAF 11 g/s, idle 820 rpm” |
| Distinguish intermittent | Freeze frame captures conditions at event, not now |

---

## Reading DTCs in this project

```powershell
conda activate small-hack-1
python -c "from obd_connection import connect; import obd; c=connect(); print('Stored:', c.query(obd.commands.GET_DTC).value); print('Pending:', c.query(obd.commands.GET_CURRENT_DTC).value); c.close()"
```

Clear after testing:

```python
c.query(obd.commands.CLEAR_DTC)
```

---

## Mapping DTCs → pipeline layers

| Layer | Role |
|-------|------|
| **XGBoost** | Primary signal = PID features; DTC optional as categorical input |
| **Rules** | Cross-check: `P0171` + positive STFT + low MAF → high confidence vacuum leak |
| **Gemma** | Plain-language explanation using code description + live PIDs + freeze frame |
| **Labels** | `ground_truth_dtc` in session CSV when emulator or car provides codes |

Prefer **PID-based labels** for training (see [fault_profiles.md](fault_profiles.md)). DTCs often appear **late** — after trims have been out of range for many drive cycles.

---

## See also

- [fault_profiles.md](fault_profiles.md) — fault OBD signatures and typical DTC per fault
- [fault_simulation.md](fault_simulation.md) — simulating DTCs on the emulator
- [test_commands.md](test_commands.md) — `GET_DTC`, `CLEAR_DTC`, discovery
- [toyota_pid_definitions.md](toyota_pid_definitions.md) — hybrid live PIDs that precede DTCs

### External references

- [SAE J2012](https://www.sae.org) — standard DTC definitions (P0/P2)
- Toyota service manual / Techstream — authoritative P1/P3 and infocodes
- [PriusChat DTC forums](https://priuschat.com) — community hybrid code experience
