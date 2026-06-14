# OBD-II PID definitions

Reference for **Parameter IDs (PIDs)** used in this project — what they measure, units, typical values, and diagnostic meaning.

**Related docs**

| Doc | Use for |
|-----|---------|
| [emulator_car_queries.md](emulator_car_queries.md) | All 86 commands the `car` emulator supports + sample values |
| [fault_profiles.md](fault_profiles.md) | Which PIDs change for each simulated fault |
| [fault_simulation.md](fault_simulation.md) | Hex encoding when building emulator overrides |

---

## What is a PID?

On OBD-II, a **PID** is a numbered data item the ECU can return over the diagnostic link.

| Mode | Purpose | Example request |
|------|---------|-----------------|
| **01** | Live sensor data | `01 0C` → engine RPM |
| **03** | Stored trouble codes | `03` → DTC list |
| **07** | Pending DTCs | Current/last cycle |

In **Mode 01**, the scan tool sends `01 XX` where `XX` is the PID hex code. The ECU replies with `41 XX` plus encoded bytes. python-OBD wraps this as named commands (`obd.commands.RPM`, etc.).

```text
Request:  01 0C          (Mode 01, PID 0x0C = RPM)
Response: 41 0C 14 50    (RPM = 0x1450 / 4 = 1300 rpm)
```

Not every vehicle exposes every PID. The emulator `car` scenario supports **86 commands** — see [emulator_car_queries.md](emulator_car_queries.md).

---

## Naming conventions

| Prefix | Meaning |
|--------|---------|
| *(none)* | Live value (Mode 01) |
| `DTC_` | Freeze-frame snapshot stored when a DTC set (Mode 02) |
| `PIDS_A` / `B` / `C` | Bitmask of which PIDs the ECU supports |

**Bank / sensor suffixes**

| Suffix | Meaning |
|--------|---------|
| `_1` | Bank 1 (most 4-cylinder engines have one bank) |
| `B1S1` | Bank 1, sensor 1 (upstream / pre-cat O2) |
| `B1S2` | Bank 1, sensor 2 (downstream / post-cat O2) |
| `S1_WR` | Wide-range O2 sensor (lambda), sensor 1 |

---

## Core PIDs (streaming pipeline)

These are the primary inputs for feature extraction and fault detection in this repo.

### Engine speed and load

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| Engine RPM | `0x0C` | `RPM` | rpm | Crankshaft speed. Idle ~700–900; cruise ~1500–3000. |
| Vehicle speed | `0x0D` | `SPEED` | km/h | From wheel speed sensor. 0 = stopped. |
| Calculated engine load | `0x04` | `ENGINE_LOAD` | % | ECU estimate of current torque vs maximum. High under acceleration. |
| Absolute load | `0x43` | `ABSOLUTE_LOAD` | % | Normalized load including barometric correction. |
| Timing advance | `0x0E` | `TIMING_ADVANCE` | degrees BTDC | Spark timing before top dead center. Negative = retarded. |

**Diagnostic use:** RPM + speed together distinguish idle, cruise, and slip-like conditions. Load separates light vs heavy demand. Unstable RPM at constant speed suggests misfire.

---

### Air and fuel metering

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| Mass airflow | `0x10` | `MAF` | g/s | Air mass entering the engine. Primary load indicator on MAF-based systems. |
| Intake manifold pressure | `0x0B` | `INTAKE_PRESSURE` | kPa | Absolute pressure in intake. High vacuum (low kPa) at idle; rises with throttle. |
| Intake air temperature | `0x0F` | `INTAKE_TEMP` | °C | Air temp at intake. Should be plausible vs ambient and coolant after warm-up. |
| Throttle position | `0x11` | `THROTTLE_POS` | % | Driver throttle pedal / plate angle. |
| Relative throttle | `0x45` | `RELATIVE_THROTTLE_POS` | % | Throttle relative to learned minimum. |
| Commanded equiv. ratio | `0x44` | `COMMANDED_EQUIV_RATIO` | ratio | Target air/fuel ratio (1.0 = stoichiometric). |

**Diagnostic use:** MAF should correlate with RPM and load. Low MAF with positive fuel trim → vacuum leak or dirty MAF. MAP inconsistent with RPM/throttle → MAP sensor fault. High throttle + low MAF + low speed → restriction or catalyst clog.

---

### Fuel trims

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| Short-term fuel trim B1 | `0x06` | `SHORT_FUEL_TRIM_1` | % | Immediate fuel correction from O2 feedback. Changes quickly. |
| Long-term fuel trim B1 | `0x07` | `LONG_FUEL_TRIM_1` | % | Learned correction stored by ECU. Changes slowly over trips. |

**How to read values**

- **0%** = ECU not adding or removing fuel beyond base map.
- **Positive (+)** = ECU adding fuel → mixture was **lean** (unmetered air, weak fuel delivery, etc.).
- **Negative (−)** = ECU removing fuel → mixture was **rich** (leaking injector, stuck purge, etc.).

Typical healthy range: roughly **±10%**. Sustained **±15–25%** often triggers lean/rich DTCs.

**Encoding:** Stored as a byte where `0x80` = 0%. Formula: `percent = (byte − 128) × 100 / 128`.

| Trim | Byte (hex) |
|------|------------|
| 0% | `80` |
| +15% | `93` |
| +20% | `9A` |
| −15% | `6D` |
| −20% | `66` |

**Diagnostic use:** STFT reacts first; LTFT confirms persistent problems. Rising LTFT over weeks → gradual sensor wear or restriction.

---

### Cooling system

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| Coolant temperature | `0x05` | `COOLANT_TEMP` | °C | Engine coolant temp at ECT sensor. |
| Engine run time | `0x1F` | `RUN_TIME` | s | Seconds since engine start (this key cycle). |

**Typical values (warm gasoline engine)**

| Condition | Coolant |
|-----------|---------|
| Cold start | 20–40°C (ambient) |
| Warm idle | 85–95°C |
| Overheat | >105°C |

**Encoding:** `byte = °C + 40` (so −40°C → `0x00`, 90°C → `0x82`).

**Diagnostic use:** Coolant stuck low after long `RUN_TIME` → thermostat stuck open. Rapid rise → stuck closed or low coolant. High coolant only at idle/low speed → fan failure.

---

### Oxygen sensors and emissions

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| O2 B1S2 voltage | `0x14` | `O2_B1S2` | V | Downstream (post-catalytic) narrow-band O2. |
| O2 S1 WR voltage | `0x24` | `O2_S1_WR_VOLTAGE` | V | Upstream wide-range lambda sensor voltage. |
| O2 S1 WR current | `0x34` | `O2_S1_WR_CURRENT` | mA | Wide-range sensor pump current (lambda). |
| Commanded EGR | `0x2C` | `COMMANDED_EGR` | % | EGR valve opening commanded by ECU. |
| Evaporative purge | `0x2E` | `EVAPORATIVE_PURGE` | % | EVAP purge valve duty cycle. |
| Catalyst temp B1S1 | `0x3C` | `CATALYST_TEMP_B1S1` | °C | Estimated catalyst temperature (bank 1, sensor 1). |
| Catalyst temp B1S2 | `0x3D` | `CATALYST_TEMP_B1S2` | °C | Catalyst temperature bank 1, sensor 2. |

**O2 behavior**

| Sensor | Healthy pattern |
|--------|-----------------|
| Upstream (B1S1 / WR) | Oscillates around stoichiometric as ECU toggles fuel |
| Downstream (B1S2) | **Steady** after warm-up if catalyst is good |

Oscillating downstream O2 → catalyst efficiency loss (`P0420`). Flatlined O2 → sensor failure.

---

### Electrical

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| Control module voltage | `0x42` | `CONTROL_MODULE_VOLTAGE` | V | ECU supply voltage (alternator/charging system while running). |
| ELM adapter voltage | — | `ELM_VOLTAGE` | V | Voltage seen by the OBD adapter (not always true battery). |

**Typical values (engine running)**

| Condition | Voltage |
|-----------|---------|
| Normal charging | 13.8–14.8 V |
| Weak alternator | <13.0 V and falling |
| Overcharge | >15.5 V |

---

### Hybrid (Toyota Auris `car` scenario)

| PID | Hex | python-OBD | Unit | What it is |
|-----|-----|------------|------|------------|
| Hybrid battery remaining | `0x5B` | `HYBRID_BATTERY_REMAINING` | % | High-voltage pack state-of-health estimate (when supported). |

---

## Status and diagnostic PIDs

| Command | Mode | What it is |
|---------|------|------------|
| `GET_DTC` | 03 | Stored diagnostic trouble codes (e.g. `P0171`) |
| `GET_CURRENT_DTC` | 07 | Pending codes from current/last drive cycle |
| `CLEAR_DTC` | 04 | Clear codes and freeze frame |
| `STATUS` | 01 | MIL status, readiness monitors since last clear |
| `FUEL_STATUS` | 01 | Open/closed loop, which fuel system is active |
| `DISTANCE_W_MIL` | 01 | km driven with MIL illuminated |
| `RUN_TIME_MIL` | 01 | Minutes engine run with MIL on |
| `TIME_SINCE_DTC_CLEARED` | 01 | Minutes since codes were cleared |
| `WARMUPS_SINCE_DTC_CLEARED` | 01 | Warm-up cycles since clear |

**Freeze frame (`DTC_*` commands):** Snapshot of key PIDs at the moment a DTC was stored. Useful for validating that live fault simulation matches stored evidence.

---

## Encoding quick reference

Formulas for building emulator overrides (full list in [fault_simulation.md](fault_simulation.md)).

| PID | Command | Decode | Encode |
|-----|---------|--------|--------|
| 0x0C | `RPM` | bytes / 4 | `int(4 × rpm)` |
| 0x0D | `SPEED` | byte | `int(km/h)` |
| 0x05 | `COOLANT_TEMP` | byte − 40 | `int(°C + 40)` |
| 0x0F | `INTAKE_TEMP` | byte − 40 | `int(°C + 40)` |
| 0x0B | `INTAKE_PRESSURE` | byte | absolute kPa |
| 0x10 | `MAF` | bytes / 100 | `int(g/s × 100)` |
| 0x06/07 | Fuel trim | (byte − 128) × 100/128 | `int(128 + pct × 128/100)` |
| 0x04/11 | Load / throttle | byte × 100/255 | `int(pct × 255/100)` |
| 0x14 | `O2_B1S2` | byte / 200 | `int(V × 200)` |
| 0x42 | `CONTROL_MODULE_VOLTAGE` | bytes / 1000 | `int(V × 1000)` |
| 0x3C | `CATALYST_TEMP_B1S1` | (bytes/10) − 40 | `int((°C + 40) × 10)` |

**Raw hex probe:** at emulator `CMD>`, `test 010c` requests PID `0x0C` and prints the response.

---

## PIDs by subsystem (fault mapping)

| Subsystem | Key PIDs | See faults |
|-----------|----------|------------|
| Air intake | `MAF`, `INTAKE_PRESSURE`, `INTAKE_TEMP`, `THROTTLE_POS` | Vacuum leak, dirty MAF, filter restriction, EGR |
| Fuel | `SHORT/LONG_FUEL_TRIM_1`, `COMMANDED_EQUIV_RATIO` | Pump, injectors, purge valve |
| Ignition | `RPM`, `TIMING_ADVANCE`, `O2_B1S2` | Coil, spark plugs |
| Cooling | `COOLANT_TEMP`, `RUN_TIME`, `SPEED` | Thermostat, fan, pump, low coolant |
| Emissions | `O2_*`, `CATALYST_TEMP_*`, `EVAPORATIVE_PURGE` | Catalyst, O2 sensors |
| Electrical | `CONTROL_MODULE_VOLTAGE`, `ELM_VOLTAGE` | Alternator, battery, regulator |

Details per fault: [fault_profiles.md](fault_profiles.md).

---

## See also

- [toyota_pid_definitions.md](toyota_pid_definitions.md) — Toyota hybrid extended PIDs and ECU headers
- [toyota_dtc_definitions.md](toyota_dtc_definitions.md) — Toyota and hybrid DTC reference
- [../README.md](../README.md) — pipeline architecture and streaming PIDs list
- [test_commands.md](test_commands.md) — connect and query from Python
