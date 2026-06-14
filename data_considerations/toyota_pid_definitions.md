# Toyota PID definitions

Toyota-specific OBD access for **hybrid vehicles** — focused on the **Auris Hybrid** class (same hybrid architecture family as Prius). For generic SAE PIDs, see [pid_definitions.md](pid_definitions.md).

**Vehicle context in this repo:** ELM327-emulator `-s car` models a **Toyota Auris Hybrid** with **86 standard Mode 01** commands only. Extended Toyota PIDs below apply to **real hardware** (Torque Pro, OBD Fusion, CAN tools) — not the emulator unless you add custom responses.

---

## Standard vs Toyota extended PIDs

| Layer | Mode | Who defines it | Access in this project |
|-------|------|----------------|------------------------|
| **Generic OBD-II** | `01` | SAE J1979 | ✅ Emulator + python-OBD |
| **Toyota extended** | `21` (older) / `22` (newer) | Toyota per-ECU | ❌ Not in emulator; needs header + custom request |
| **DTCs** | `03`, `07` | SAE + Toyota | Emulator returns empty `GET_DTC` in `car` scenario |

Generic PIDs (`RPM`, `COOLANT_TEMP`, fuel trims, etc.) come from the **engine ECU** at CAN header **`7E0`**. Hybrid battery, motor, and inverter data live on **other ECUs** and require:

1. The correct **CAN receive address** (header), e.g. `7E3` for HV battery
2. Toyota **Mode 21 or 22** request with a **manufacturer PID**
3. A **decode formula** on response bytes A, B, C…

Newer Toyota hybrids (2016+) often use **Mode 22** (2-byte PID) instead of Mode 21. Always verify on your model year — a PID that works on Gen2 Prius may fail on Gen4 with response `7F 11` (mode not supported).

---

## Toyota ECU addresses (common)

| Header | ECU | Typical data |
|--------|-----|--------------|
| `7E0` | Engine control (ECM) | RPM, MAF, fuel trims, coolant, O2 |
| `7E2` | Hybrid control (HV CPU) | HV SOC summary, MG RPM/torque, boost voltage, ready-to-EV |
| `7E3` | HV battery management | Block voltages, pack current, SOC, charge/discharge limits |
| `7D2` | Hybrid system / inverter | Inverter temps, MG temps (Mode 22 on newer cars) |
| `747` | Battery ECU (some Gen4+) | SOC, pack voltage (Mode 22) |
| `7B0` | ABS / skid control | Wheel speeds (manufacturer) |
| `7C0` | Combination meter | Odometer, trip counters |

Requests are sent to `header + 8` (e.g. query `7E3` → TX ID `7E3`, RX `7EB`).

---

## Standard PIDs on Toyota hybrids (Mode 01)

These work through any ELM327 adapter and match [emulator_car_queries.md](emulator_car_queries.md).

### Engine / emissions (same as generic)

Toyota Atkinson-cycle engines expose normal Mode 01 PIDs on `7E0`: `RPM`, `SPEED`, `MAF`, `INTAKE_PRESSURE`, `SHORT_FUEL_TRIM_1`, `LONG_FUEL_TRIM_1`, `COOLANT_TEMP`, `O2_B1S2`, `O2_S1_WR_*`, catalyst temps, etc.

Fuel trim interpretation is identical to [pid_definitions.md](pid_definitions.md). Toyota tends toward **long warm-up** and **conservative trim limits** before setting lean/rich codes.

### Toyota-specific Mode 01 entries

| PID (hex) | python-OBD | Unit | Meaning |
|-----------|------------|------|---------|
| `0x5B` | `HYBRID_BATTERY_REMAINING` | % | Hybrid/EV battery **state of health / remaining life** estimate (when ECU supports it; often `NULL` on emulator) |
| `0x51` | `FUEL_TYPE` | enum | Often reports **Gasoline** on Auris Hybrid (ICE + HV system) |

### Readiness and compliance

| Command | Notes on Toyota |
|---------|-----------------|
| `OBD_COMPLIANCE` | Emulator reports **EOBD (Europe)** for `car` scenario |
| `STATUS` | Readiness monitors; Toyota may take **longer drive cycles** to set “ready” after clear |
| `FUEL_STATUS` | Closed-loop behavior; hybrid may show transitions during engine start/stop |

---

## Hybrid system — extended PIDs (real vehicle)

Community-documented PIDs for **Prius-class / Auris Hybrid** THS. Format: **Header · Mode+PID · Response decode**.

> **Auris note:** The [Auris Hybrid Torque PID list](http://zansprojects.blogspot.com/2018/12/torque-pids-for-toyota-auris-hybrid.html) (~212 working entries) was validated against a **2017 Auris** by filtering PriusChat definitions. Not every Prius PID works on Auris — test before logging.

### HV battery ECU (`7E3`) — Mode `21`

| Name | Mode+PID | Decode (Torque-style) | Unit | Typical range |
|------|----------|----------------------|------|---------------|
| HV battery state of charge | `21CE` | `0.5 × A` | % | 40–80 (display); wider internally |
| HV battery current | `21CE` | `(256×B + C) / 100 − 327.68` | A | −100 to +100 (charge/discharge) |
| HV block 1–14 voltage | `21CE` | `(256×D + E) / 100 − 327.68` per block byte pair | V | ~6–8 V per NiMH/Li block |
| HV block lowest voltage | `21D0` | `(256×J + K) / 100 − 327.68` | V | Spread >0.3 V suggests weak block |
| HV block highest voltage | `21D0` | `(256×M + N) / 100 − 327.68` | V | |
| HV block count | `21D0` | `A` | count | 14 (Prius) / 17 (some Lexus) / varies |
| HV battery intake air temp | `21CF` | `(256×A + B) / 100 − 327.68` | °C | Cooling airflow over pack |
| HV charge power limit | `21CF` | `E − 64` | kW | Max regen/charge acceptance |
| HV discharge power limit | `21CF` | `F − 64` | kW | Max discharge to motors |
| HV battery fan mode | `21CF` | `I` | enum | Forced cooling status |

**Derived:** Battery power (kW) ≈ `HV current × sum(block voltages) / 1000`.

**Diagnostic use:** Block voltage **spread** (max − min) is the primary HV battery health indicator. Large spread under load → weak module. SOC alone is not SOH.

### Hybrid control ECU (`7E2`) — Mode `21`

| Name | Mode+PID | Decode | Unit | Notes |
|------|----------|--------|------|-------|
| HV SOC (alt) | `21C3` | `0.392 × S` | % | May differ from `7E3` SOC |
| Voltage before boost | `21C4` | `2 × D` | V | DC link before boost converter |
| Voltage after boost | `21C4` | `2 × E` | V | Boosted HV rail (~200–650 V class) |
| MG1 / MG2 RPM, torque | `21C3` / related | varies | rpm, Nm | Motor/generator speeds; model-specific bytes |

These PIDs report **power split** between ICE, MG1 (generator/motor), and MG2 (drive motor). Useful for distinguishing EV-mode driving vs engine-on hybrid.

### Newer platforms — Mode `22` (examples, Gen4 Prius class)

| Name | Mode+PID | Header | Decode | Notes |
|------|----------|--------|--------|-------|
| Hybrid battery SOC | `227A76` | `747` | `A × 20 / 51` | % |
| Hybrid battery voltage | `227A53` | `747` | `C × 4` | V |
| Inverter coolant temp | `221093` | `7D2` | `A × 9/5 − 40` | °C (formula often listed in °F in forums) |
| Generator inverter temp | `221089` | `7D2` | `A × 9/5 − 40` | °C |
| Boost converter temp (upper/lower) | `2210AB` | `7D2` | `A` or `B` × 9/5 − 40 | °C |

**Auris 2017 (E18):** Likely Mode **21** on `7E3`/`7E2` (Prius-family), not Gen4 Mode 22 — confirm with a single PID scan before relying on Gen4 tables.

---

## ICE behavior on Toyota hybrids (diagnostic context)

| Behavior | OBD implication |
|----------|-----------------|
| Engine auto stop at lights | RPM → 0 while `SPEED` = 0; coolant may creep up in traffic |
| Engine start for HV charge | RPM rises at standstill; MAF nonzero; not a idle fault |
| EV mode | ICE off; no MAF; battery current negative (discharge) on `7E3` |
| Warm-up request | ICE held running until catalyst warm; affects fuel trims temporarily |

When simulating faults on the emulator, do not mislabel normal hybrid stop/start as misfire unless RPM is **erratic** while the ICE is supposed to be running steadily.

---

## What the emulator exposes today

The `car` scenario implements **standard Mode 01 only** — see [emulator_car_queries.md](emulator_car_queries.md).

| Toyota-relevant command | Emulator sample | Extended? |
|-------------------------|-----------------|-----------|
| `HYBRID_BATTERY_REMAINING` | NULL | Mode 01 placeholder |
| `RPM`, `SPEED`, `MAF`, trims, coolant, O2 | ✅ live values | No |
| HV SOC, block voltages, MG temps | ❌ not available | Needs Mode 21/22 + header |
| Transmission temps | ❌ not in 86-command list | Manufacturer PIDs |

For pipeline v1, train on **ICE-side PIDs** from the emulator. Plan Mode 22 integration separately for HV battery health on real cars.

---

## Accessing Toyota PIDs in software

| Tool | Toyota extended PIDs |
|------|----------------------|
| **Torque Pro** | Custom PID CSV; predefined “Prius Gen 3” set; [Auris-filtered list](http://zansprojects.blogspot.com/2018/12/torque-pids-for-torque-auris-hybrid.html) |
| **OBD Fusion** | Toyota hybrid add-on (handles headers/modes) |
| **python-OBD** | Mode 01 only out of the box; Mode 21/22 needs raw ELM commands (`AT SH 7E3`, custom request bytes) |
| **Carista / Techstream** | Full Toyota dealer diagnostics (not OBD-generic) |

**Raw request shape (conceptual):**

```text
AT SH 7E3          # set header to HV battery ECU
21 CE 1            # Mode 21, PID CE, 1 byte (Toyota convention in Torque)
                   # Response: 61 CE [bytes A B C D ...]
```

Do not send untested Mode 22 writes. Read-only PID queries are safe; incorrect **write** commands can affect ECU behavior.

---

## Quick reference — HV battery health

| Signal | Source | Healthy indicator | Concern |
|--------|--------|-------------------|---------|
| Block voltage spread | `7E3` `21D0` / `21CE` | < ~0.15 V at steady SOC | > 0.3 V → weak block/module |
| SOC | `7E3` `21CE` | 40–80% normal driving | Stuck high/low with current mismatch |
| Pack current | `7E3` `21CE` | Matches driver demand | Unexpected discharge at rest |
| Battery temp | `7E3` `21CF` | Stable, below limit | Sustained high → fan/limiting power |
| Charge/discharge limits | `7E3` `21CF` | Symmetric, reasonable | Severely reduced limits → protection mode |

---

## DTC definitions

Toyota powertrain and hybrid trouble codes are documented in [toyota_dtc_definitions.md](toyota_dtc_definitions.md). Full diagnosis of HV block faults often needs Techstream — OBD PIDs alone may not isolate a failing block.

---

## See also

- [toyota_dtc_definitions.md](toyota_dtc_definitions.md) — Toyota and hybrid DTC reference
- [pid_definitions.md](pid_definitions.md) — generic Mode 01 PID meanings and encoding
- [emulator_car_queries.md](emulator_car_queries.md) — all 86 commands in `car` scenario
- [fault_profiles.md](fault_profiles.md) — fault signatures on standard PIDs
- [test_commands.md](test_commands.md) — emulator connection and discovery

### External references

- [Torque PIDs for Toyota Auris Hybrid (2017)](http://zansprojects.blogspot.com/2018/12/torque-pids-for-toyota-auris-hybrid.html) — Auris-validated CSV
- [PriusChat custom PID threads](https://priuschat.com) — community Mode 21/22 formulas
- [Prius Gen2 CAN/OBD2 PID compilation (PDF)](https://attachments.priuschat.com/attachment-files/2021/09/211662_Prius22009_CAnCodes.pdf) — header and byte layouts
