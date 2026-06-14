# Fault simulation guide

How to simulate automotive faults in the **ELM327-emulator** `car` scenario for training and testing the OBD Intelligence pipeline.

**Prerequisites:** emulator running (`elm327-emulator -s car -n 35000`), Python env `small-hack-1`. See [test_commands.md](test_commands.md). For OBD signatures without code, see [fault_profiles.md](fault_profiles.md).

---

## Simulation philosophy

Simulate the **causal chain**, not just a DTC string:

```text
Fault → physical effect → sensor readings → ECU compensation → OBD PIDs → (optional) DTC
```

Example — vacuum leak:

```text
Unmetered air → lean mixture → STFT/LTFT rise → P0171 (eventually)
```

Your detector should learn from **PID patterns over time** (mean / std / slope). DTCs are a bonus layer, not the primary training signal.

---

## How to apply overrides

All commands below are typed at the emulator **`CMD>`** prompt (Terminal 1).

### Set a PID override

```python
emulator.answer['RPM'] = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * 1300)</exec><writeln />'
```

### Verify with raw hex

```
test 010c
```

### Verify with Python (Terminal 2)

```powershell
cd scratch_code
python -c "from obd_connection import connect; import obd; c=connect(); print(c.query(obd.commands.RPM).value); c.close()"
```

### Clear one override

```python
del emulator.answer['RPM']
```

### Clear all overrides

```
reset
```

### Keys must match python-OBD command names

Use the names from [emulator_car_queries.md](emulator_car_queries.md): `RPM`, `SPEED`, `COOLANT_TEMP`, `SHORT_FUEL_TRIM_1`, `LONG_FUEL_TRIM_1`, `MAF`, `INTAKE_PRESSURE`, `INTAKE_TEMP`, `ENGINE_LOAD`, `THROTTLE_POS`, `O2_B1S2`, `O2_S1_WR_VOLTAGE`, `CONTROL_MODULE_VOLTAGE`, `COMMANDED_EGR`, `EVAPORATIVE_PURGE`, `CATALYST_TEMP_B1S1`, `CATALYST_TEMP_B1S2`, etc.

---

## OBD encoding cheat sheet

Use these when building `<exec>` strings. Formulas match SAE J1979 / python-OBD decoding.

| PID | Command | Encode value → hex byte(s) |
|-----|---------|----------------------------|
| 0x0C | `RPM` | `int(4 * rpm)` → 2 bytes, e.g. 1300 rpm → `1450` |
| 0x0D | `SPEED` | `int(kmh)` → 1 byte, e.g. 10 → `0A` |
| 0x05 | `COOLANT_TEMP` | `int(degC + 40)` → 1 byte, e.g. 90°C → `82` |
| 0x0F | `INTAKE_TEMP` | `int(degC + 40)` → 1 byte |
| 0x0B | `INTAKE_PRESSURE` | `int(kPa)` absolute → 1 byte |
| 0x10 | `MAF` | `int(gps * 100)` → 2 bytes, e.g. 16 g/s → `0640` |
| 0x06 | `SHORT_FUEL_TRIM_1` | `int(128 + pct * 128 / 100)` → 1 byte |
| 0x07 | `LONG_FUEL_TRIM_1` | same as STFT |
| 0x04 | `ENGINE_LOAD` | `int(pct * 255 / 100)` → 1 byte |
| 0x11 | `THROTTLE_POS` | `int(pct * 255 / 100)` → 1 byte |
| 0x14 | `O2_B1S2` | `int(volts * 200)` → 1 byte |
| 0x42 | `CONTROL_MODULE_VOLTAGE` | `int(volts * 1000)` → 2 bytes |
| 0x2C | `COMMANDED_EGR` | `int(pct * 255 / 100)` → 1 byte |
| 0x2E | `EVAPORATIVE_PURGE` | `int(pct * 255 / 100)` → 1 byte |
| 0x3C | `CATALYST_TEMP_B1S1` | `int((degC + 40) * 10)` → 2 bytes |

**Fuel trim examples**

| Trim | Byte (hex) |
|------|------------|
| 0% | `80` |
| +15% | `93` |
| +20% | `9A` |
| −15% | `6D` |
| −20% | `66` |

**Copy-paste helpers** (run at `CMD>` to define once per session):

```python
def trim_b(p): return int(128 + p * 128 / 100)
def maf_h(g): return "%.4X" % int(g * 100)
def clt_b(t): return "%.2X" % int(t + 40)
def rpm_h(r): return "%.4X" % int(4 * r)
def volt_h(v): return "%.4X" % int(v * 1000)
```

---

## Recording training sessions

After applying a fault profile:

1. **Label** the session in your log metadata, e.g. `fault=vacuum_leak`, `scenario=idle`.
2. Stream from Python at ~1 Hz for **5+ minutes** (feature window length).
3. Save CSV: timestamp + all PIDs in `obd_connection.py` `PIDS` list.
4. Run `reset` or `del emulator.answer[...]` before the next fault.

Suggested columns for synthetic labels:

| Field | Example |
|-------|---------|
| `session_id` | `vacuum_leak_idle_001` |
| `fault_class` | `vacuum_leak` |
| `driving_context` | `idle` / `cruise` / `wot` |
| `ground_truth_dtc` | `P0171` or empty |

---

## Priority faults (start here)

| Fault | Difficulty | Training value | Section |
|-------|------------|----------------|---------|
| Vacuum leak | Easy | High | [#1](#1-vacuum-leak) |
| Dirty MAF | Easy | High | [#2](#2-dirty-maf-sensor) |
| Thermostat stuck open | Easy | High | [#11](#11-thermostat-stuck-open) |
| Cooling fan failure | Easy | High | [#13](#13-cooling-fan-failure) |
| Alternator failure | Easy | High | [#25](#25-alternator-failure) |
| Weak fuel pump | Medium | High | [#5](#5-fuel-pump-weakening) |
| Injector leak | Medium | High | [#7](#7-leaking-injector) |
| O2 sensor drift | Medium | High | [#19](#19-o2-sensor-drift) |
| Catalytic degradation | Medium | High | [#16](#16-catalytic-converter-degradation) |
| Head gasket leak | Hard | High | [#29](#29-head-gasket-leak) |
| Timing chain stretch | Hard | Very high | [#30](#30-timing-chain-stretch) |

---

# Air system

## 1. Vacuum leak

**Cause:** Unmetered air (cracked hose, PCV leak, intake gasket).

**OBD signature**

```text
STFT ↑↑   LTFT ↑↑   MAF lower than expected   idle RPM slightly high
```

**Simulate (idle, `SPEED` = 0)**

```python
scenario car
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(20)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(15)</exec><writeln />'
emulator.answer['MAF']               = '<exec>ECU_R_ADDR_E + " 04 41 10 " + maf_h(12)</exec><writeln />'
emulator.answer['INTAKE_PRESSURE']   = '<exec>ECU_R_ADDR_E + " 03 41 0B 37</exec><writeln />'
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(950)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 00</exec><writeln />'
```

**Verify:** `test 0106`, `test 0107`, `test 0110` — STFT ~+20%, LTFT ~+15%, MAF ~12 g/s.

**Typical DTC:** `P0171` System Too Lean (Bank 1).

**LLM hint:** *Likely vacuum leak; most noticeable at idle with positive trims and low MAF.*

---

## 2. Dirty MAF sensor

**Cause:** MAF underestimates airflow.

**OBD signature**

```text
MAF low vs RPM/load   LTFT +   STFT +
```

At higher RPM, MAF should be ~25 g/s but reads ~16 g/s.

**Simulate (cruise)**

```python
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(2500)</exec><writeln />'
emulator.answer['ENGINE_LOAD']       = '<exec>ECU_R_ADDR_E + " 03 41 04 80</exec><writeln />'
emulator.answer['MAF']               = '<exec>ECU_R_ADDR_E + " 04 41 10 " + maf_h(16)</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(12)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(10)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 50</exec><writeln />'
```

**Typical DTC:** `P0101` MAF Range/Performance.

---

## 3. Air filter restriction

**Cause:** Blocked airflow — sluggish, needs more throttle for same power.

**OBD signature**

```text
Throttle ↑   MAF ↓   Engine load ↓ (at same RPM)
```

**Simulate**

```python
emulator.answer['THROTTLE_POS'] = '<exec>ECU_R_ADDR_E + " 03 41 11 A0</exec><writeln />'
emulator.answer['MAF']          = '<exec>ECU_R_ADDR_E + " 04 41 10 " + maf_h(35)</exec><writeln />'
emulator.answer['ENGINE_LOAD']  = '<exec>ECU_R_ADDR_E + " 03 41 04 45</exec><writeln />'
emulator.answer['RPM']          = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(2200)</exec><writeln />'
emulator.answer['SPEED']        = '<exec>ECU_R_ADDR_E + " 03 41 0D 35</exec><writeln />'
```

**Note:** Best detected by comparing throttle vs MAF vs speed over time (sluggish acceleration profile). Run two sessions: healthy cruise vs restricted filter.

---

## 4. Stuck open EGR

**Cause:** Exhaust gas enters intake continuously.

**OBD signature**

```text
Rough idle   RPM unstable   possible STFT +
```

**Simulate (unstable idle)**

```python
emulator.answer['COMMANDED_EGR']     = '<exec>ECU_R_ADDR_E + " 03 41 2C FF</exec><writeln />'
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(600, 1100))</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(8)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 00</exec><writeln />'
```

**Typical DTC:** `P0401` EGR insufficient flow (stuck closed) or rough-idle misfire codes when severe.

---

# Fuel system

## 5. Fuel pump weakening

**Cause:** Low fuel pressure under load.

**OBD signature**

```text
Idle: normal trims   Under load: STFT +20%, LTFT +15%
```

**Simulate as two labeled sessions** (emulator overrides are static; load-dependence = different sessions).

**Session A — idle (healthy)**

```python
reset
scenario car
# defaults OK; or explicitly trim_b(0)
```

**Session B — heavy acceleration (weak pump)**

```python
emulator.answer['ENGINE_LOAD']       = '<exec>ECU_R_ADDR_E + " 03 41 04 FF</exec><writeln />'
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(4500)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 90</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(20)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(15)</exec><writeln />'
```

**Typical DTC:** `P0171` under load; may be intermittent.

---

## 6. Dirty fuel injectors

**Cause:** Reduced spray — uneven combustion.

**OBD signature**

```text
Positive trims   RPM instability (mild)
```

**Simulate**

```python
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(14)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(11)</exec><writeln />'
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(1100, 1350))</exec><writeln />'
```

**Typical DTC:** `P0300` random misfire (when severe).

---

## 7. Leaking injector

**Cause:** Continuous fuel drip — rich condition.

**OBD signature**

```text
STFT −   LTFT −   (negative trims)
```

**Simulate**

```python
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(-18)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(-12)</exec><writeln />'
emulator.answer['COMMANDED_EQUIV_RATIO'] = '<exec>ECU_R_ADDR_E + " 04 41 44 00 90</exec><writeln />'
```

**Typical DTC:** `P0172` System Too Rich.

---

## 8. Injector stuck closed

**Cause:** One cylinder lean → misfire.

**OBD signature**

```text
Positive trims   RPM instability
```

**Simulate** (same as misfire + lean trims)

```python
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(16)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(8)</exec><writeln />'
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(750, 1250))</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 00</exec><writeln />'
```

**Typical DTC:** `P0301`–`P0304` cylinder-specific misfire.

---

# Ignition system

## 9. Ignition coil failure

**Cause:** Weak spark on one cylinder.

**OBD signature**

```text
RPM instability   misfire tendency   O2 swings   trims may go positive
```

**Simulate**

```python
emulator.answer['RPM'] = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(500, 1500))</exec><writeln />'
emulator.answer['O2_B1S2'] = '<exec>ECU_R_ADDR_E + " 03 41 14 %.2X" % randint(10, 200)</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(6)</exec><writeln />'
emulator.answer['SPEED'] = '<exec>ECU_R_ADDR_E + " 03 41 0D 00</exec><writeln />'
```

**Training tip:** High **std** on RPM over 5 min at idle is the strongest feature.

**Typical DTC:** `P0301` (cylinder 1 misfire).

---

## 10. Spark plug wear

**Cause:** Gradual ignition efficiency loss.

**OBD signature**

```text
Slowly increasing fuel trims   reduced performance
```

**Simulate as a time series** — run 3 sessions with escalating LTFT:

| Session | LTFT override |
|---------|---------------|
| `spark_plug_early` | `trim_b(4)` |
| `spark_plug_mid` | `trim_b(9)` |
| `spark_plug_late` | `trim_b(14)` |

```python
emulator.answer['LONG_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(9)</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(6)</exec><writeln />'
```

**Training tip:** Label by week/sessions; model learns **positive slope** on LTFT.

---

# Cooling system

## 11. Thermostat stuck open

**Cause:** Engine never reaches operating temperature.

**OBD signature**

```text
Coolant temp low after long run   e.g. 65°C after 15 min (expect ~90°C)
```

**Simulate**

```python
emulator.answer['COOLANT_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 05 " + clt_b(65)</exec><writeln />'
emulator.answer['RUN_TIME']     = '<exec>ECU_R_ADDR_E + " 04 41 1F 0E 10</exec><writeln />'
```

(`RUN_TIME` ≈ 3600 s encoded in 2 bytes — adjust as needed.)

**Typical DTC:** `P0128` Coolant Thermostat (often).

**LLM hint:** *Engine not reaching operating temperature; stuck-open thermostat suspected.*

---

## 12. Thermostat stuck closed

**Cause:** Coolant cannot circulate — rapid overheating.

**OBD signature**

```text
Coolant temp rapidly rising → 105°C, 110°C, 115°C
```

**Simulate rising temp** (step through 3 short sessions, or one session with manual edits):

```python
# Session: overheating_critical
emulator.answer['COOLANT_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 05 " + clt_b(112)</exec><writeln />'
emulator.answer['SPEED']        = '<exec>ECU_R_ADDR_E + " 03 41 0D 25</exec><writeln />'
```

For **slope feature** training, record sessions at 85°C → 95°C → 105°C → 112°C (change override every 2 min while streaming).

**Typical DTC:** `P0217` Engine Coolant Over Temperature.

---

## 13. Cooling fan failure

**Cause:** No airflow at low speed — overheats at idle/traffic only.

**OBD signature**

```text
Normal while moving   Overheats at idle / traffic lights
```

**Simulate as two sessions** (static emulator cannot read other PIDs in one override):

| Session | `SPEED` | `COOLANT_TEMP` |
|---------|---------|------------------|
| `fan_fail_cruise` | 60 km/h | 88°C |
| `fan_fail_idle` | 0 km/h | 108°C |

**Idle / traffic session**

```python
emulator.answer['SPEED']        = '<exec>ECU_R_ADDR_E + " 03 41 0D 00</exec><writeln />'
emulator.answer['COOLANT_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 05 " + clt_b(108)</exec><writeln />'
emulator.answer['RPM']          = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(750)</exec><writeln />'
```

**Training tip:** Feature = high coolant **only when** speed mean < 5 km/h.

---

## 14. Water pump degradation

**Cause:** Reduced circulation — gradual overheating under load.

**OBD signature**

```text
Temp slowly increasing   worse at high load / high RPM
```

**Simulate (high load)**

```python
emulator.answer['RPM']          = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(3800)</exec><writeln />'
emulator.answer['ENGINE_LOAD']  = '<exec>ECU_R_ADDR_E + " 03 41 04 C0</exec><writeln />'
emulator.answer['COOLANT_TEMP']  = '<exec>ECU_R_ADDR_E + " 03 41 05 " + clt_b(102)</exec><writeln />'
```

Pair with a **healthy baseline** session at same RPM/load with COOLANT ~88°C.

---

## 15. Low coolant

**OBD signature**

```text
Unstable temperature   overheating spikes
```

**Simulate (unstable coolant)**

```python
emulator.answer['COOLANT_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 05 %.2X" % int(85 + randint(-8, 25))</exec><writeln />'
```

**Training tip:** High **std** on coolant temp distinguishes this from stuck-closed thermostat (steady high slope).

---

# Emissions system

## 16. Catalytic converter degradation

**Cause:** Catalyst aging — downstream O2 should oscillate like upstream (unhealthy).

**OBD signature**

```text
Upstream O2 oscillates   Downstream O2 also oscillates (healthy: downstream stable)
```

**Simulate (oscillating downstream O2)**

```python
emulator.answer['O2_B1S2'] = '<exec>ECU_R_ADDR_E + " 03 41 14 %.2X" % randint(30, 170)</exec><writeln />'
emulator.answer['O2_S1_WR_VOLTAGE'] = '<exec>ECU_R_ADDR_E + " 04 41 24 %.4X" % randint(200, 3500)</exec><writeln />'
```

**Healthy baseline:** fix `O2_B1S2` to a steady mid value:

```python
emulator.answer['O2_B1S2'] = '<exec>ECU_R_ADDR_E + " 03 41 14 80</exec><writeln />'
```

**Typical DTC:** `P0420` Catalyst Efficiency Below Threshold.

---

## 17. Catalytic converter restriction

**Cause:** Clogged catalyst — low power, high exhaust backpressure.

**OBD signature**

```text
High load   Low MAF   Poor acceleration   Catalyst temp ↑
```

**Simulate**

```python
emulator.answer['ENGINE_LOAD']       = '<exec>ECU_R_ADDR_E + " 03 41 04 F0</exec><writeln />'
emulator.answer['MAF']               = '<exec>ECU_R_ADDR_E + " 04 41 10 " + maf_h(28)</exec><writeln />'
emulator.answer['RPM']                = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(2800)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 40</exec><writeln />'
emulator.answer['CATALYST_TEMP_B1S1'] = '<exec>ECU_R_ADDR_E + " 04 41 3C 23 28</exec><writeln />'
```

**Typical DTC:** `P0420` / power loss complaints (may not set immediately).

---

## 18. EVAP purge valve stuck open

**Cause:** Fuel vapors enter intake at wrong time.

**OBD signature**

```text
At idle: fuel trims positive   worse after refueling
```

**Simulate**

```python
emulator.answer['EVAPORATIVE_PURGE'] = '<exec>ECU_R_ADDR_E + " 03 41 2E FF</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(14)</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(6)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 00</exec><writeln />'
```

**Typical DTC:** `P0441` EVAP Incorrect Purge Flow.

---

# Sensors

## 19. O2 sensor drift

**Cause:** Sensor aging — trims drift without obvious mechanical fault.

**OBD signature**

```text
LTFT slowly drifting   O2 less responsive
```

**Simulate** (mild trim + sluggish O2)

```python
emulator.answer['LONG_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(10)</exec><writeln />'
emulator.answer['O2_B1S2'] = '<exec>ECU_R_ADDR_E + " 03 41 14 %.2X" % (128 + randint(-5, 5))</exec><writeln />'
```

Run multiple sessions with LTFT 6% → 10% → 14% for drift slope labels.

**Typical DTC:** `P0136` O2 Circuit (B1S2) when severe.

---

## 20. O2 sensor failure

**Cause:** Sensor dead — flatlined voltage.

**OBD signature**

```text
O2 stuck at 0V or 1V continuously
```

**Simulate (stuck low)**

```python
emulator.answer['O2_B1S2'] = '<exec>ECU_R_ADDR_E + " 03 41 14 00</exec><writeln />'
```

**Stuck high**

```python
emulator.answer['O2_B1S2'] = '<exec>ECU_R_ADDR_E + " 03 41 14 C8</exec><writeln />'
```

**Training tip:** O2 **std ≈ 0** over 5 min is the tell.

---

## 21. Intake air temperature sensor failure

**OBD signature**

```text
IAT = -40°C or 120°C (implausible)
```

**Simulate**

```python
emulator.answer['INTAKE_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 0F 00</exec><writeln />'
```

or hot stuck:

```python
emulator.answer['INTAKE_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 0F A0</exec><writeln />'
```

**Typical DTC:** `P0112` / `P0113` IAT Circuit Low/High.

---

## 22. Coolant temperature sensor failure

**OBD signature**

```text
Coolant = -40°C when engine is warm   → ECU runs rich
```

**Simulate**

```python
emulator.answer['COOLANT_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 05 00</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(-10)</exec><writeln />'
```

**Typical DTC:** `P0117` ECT Circuit Low.

---

## 23. MAP sensor failure

**OBD signature**

```text
INTAKE_PRESSURE inconsistent with RPM, throttle, MAF
```

**Simulate** (high RPM but vacuum reads like idle)

```python
emulator.answer['RPM']             = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(3000)</exec><writeln />'
emulator.answer['THROTTLE_POS']    = '<exec>ECU_R_ADDR_E + " 03 41 11 70</exec><writeln />'
emulator.answer['INTAKE_PRESSURE'] = '<exec>ECU_R_ADDR_E + " 03 41 0B 95</exec><writeln />'
emulator.answer['MAF']             = '<exec>ECU_R_ADDR_E + " 04 41 10 " + maf_h(45)</exec><writeln />'
```

**Typical DTC:** `P0106` MAP Performance.

---

## 24. Throttle position sensor failure

**OBD signature**

```text
RPM changes but throttle reading stuck
```

**Simulate**

```python
emulator.answer['THROTTLE_POS'] = '<exec>ECU_R_ADDR_E + " 03 41 11 20</exec><writeln />'
emulator.answer['RPM']          = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(900, 2500))</exec><writeln />'
```

**Typical DTC:** `P0122` / `P0123` TPS Circuit.

---

# Electrical system

## 25. Alternator failure

**Cause:** Charging system cannot maintain voltage.

**OBD signature**

```text
Voltage falling while running: 14.4 → 13.8 → 13.1 → 12.7 V
```

**Simulate** (degraded charging)

```python
emulator.answer['CONTROL_MODULE_VOLTAGE'] = '<exec>ECU_R_ADDR_E + " 04 41 42 " + volt_h(12.7)</exec><writeln />'
emulator.answer['RPM']                     = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(1100)</exec><writeln />'
```

Record a **voltage descent series** as separate sessions: 14.4, 13.8, 13.1, 12.7 V for slope training.

**Typical DTC:** `P0562` System Voltage Low.

---

## 26. Weak battery

**OBD signature**

```text
Engine off: 12.6 → 12.3 → 11.9 V (trend)
```

**Note:** `CONTROL_MODULE_VOLTAGE` with engine running reflects alternator more than battery. Use `ELM_VOLTAGE` for adapter-reported supply, or `scenario engineoff` + voltage reads if your adapter supports key-on/engine-off.

**Simulate (marginal supply)**

```python
emulator.answer['ELM_VOLTAGE'] = '<writeln>11.9V</writeln>'
```

**Training tip:** Trend detection across key-on events; harder with emulator alone.

---

## 27. Voltage regulator failure

**OBD signature**

```text
15 V+ while running
```

**Simulate**

```python
emulator.answer['CONTROL_MODULE_VOLTAGE'] = '<exec>ECU_R_ADDR_E + " 04 41 42 " + volt_h(15.8)</exec><writeln />'
```

**Typical DTC:** `P0563` System Voltage High.

---

# Mechanical engine

## 28. Engine compression loss

**Cause:** Ring/valve wear — indirect OBD signs only.

**OBD signature**

```text
Abnormal trims   misfires   poor power (low MAF at high throttle)
```

**Simulate (weak power + misfire)**

```python
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(700, 1300))</exec><writeln />'
emulator.answer['ENGINE_LOAD']       = '<exec>ECU_R_ADDR_E + " 03 41 04 30</exec><writeln />'
emulator.answer['THROTTLE_POS']      = '<exec>ECU_R_ADDR_E + " 03 41 11 C0</exec><writeln />'
emulator.answer['MAF']               = '<exec>ECU_R_ADDR_E + " 04 41 10 " + maf_h(22)</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(10)</exec><writeln />'
```

**Difficulty:** Hard — label as advanced; combine multiple weak signals.

---

## 29. Head gasket leak

**OBD signature**

```text
Coolant unstable   misfires   overheating
```

**Simulate (combined)**

```python
emulator.answer['COOLANT_TEMP'] = '<exec>ECU_R_ADDR_E + " 03 41 05 %.2X" % int(95 + randint(0, 20))</exec><writeln />'
emulator.answer['RPM']          = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * randint(650, 1200))</exec><writeln />'
emulator.answer['SHORT_FUEL_TRIM_1'] = '<exec>ECU_R_ADDR_E + " 03 41 06 %.2X" % trim_b(8)</exec><writeln />'
```

**Typical DTC:** `P0300` + overheating-related codes; real diagnosis often needs exhaust gas in coolant (not on OBD).

---

## 30. Timing chain stretch

**OBD signature**

```text
Subtle: reduced performance   fuel economy loss   timing anomalies
```

**Simulate (subtle)**

```python
emulator.answer['TIMING_ADVANCE']    = '<exec>ECU_R_ADDR_E + " 03 41 0E 18</exec><writeln />'
emulator.answer['LONG_FUEL_TRIM_1']  = '<exec>ECU_R_ADDR_E + " 03 41 07 %.2X" % trim_b(7)</exec><writeln />'
emulator.answer['ENGINE_LOAD']       = '<exec>ECU_R_ADDR_E + " 03 41 04 55</exec><writeln />'
emulator.answer['RPM']               = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(2400)</exec><writeln />'
emulator.answer['SPEED']             = '<exec>ECU_R_ADDR_E + " 03 41 0D 55</exec><writeln />'
```

**Difficulty:** Hard — use as LLM reasoning / low-confidence XGBoost class; compare against healthy baseline at same speed/RPM.

---

# Transmission / drivetrain

Standard OBD-II on the `car` scenario exposes **limited** transmission data. You can still proxy some conditions:

| Symptom | Proxy simulation |
|---------|------------------|
| Slipping / high RPM no speed | High `RPM`, low `SPEED` increase across sessions |
| Converter shudder | `RPM` oscillation at steady `SPEED` |

**Example — high RPM, low speed (slip-like)**

```python
emulator.answer['RPM']   = '<exec>ECU_R_ADDR_E + " 04 41 0C " + rpm_h(4200)</exec><writeln />'
emulator.answer['SPEED'] = '<exec>ECU_R_ADDR_E + " 03 41 0D 25</exec><writeln />'
emulator.answer['ENGINE_LOAD'] = '<exec>ECU_R_ADDR_E + " 03 41 04 90</exec><writeln />'
```

**Note:** Real transmission diagnosis usually needs manufacturer-specific PIDs (not in the 86-command `car` list).

---

# Optional: simulating DTCs

The clean `car` scenario returns `GET_DTC: []`. For v1 training, **PID signatures are enough**. When you want DTC + freeze-frame testing:

1. Try the emulator `edit` command on the GET_DTC response (see [ELM327-emulator README](https://github.com/Ircama/ELM327-emulator)).
2. Or patch `obd_message.py` in your local emulator install for persistent Mode 03 responses.
3. Set matching `DTC_*` freeze-frame overrides alongside live PID faults.

Example causal pairing:

| Fault | Live PIDs | Typical DTC |
|-------|-----------|-------------|
| Vacuum leak | STFT/LTFT +, MAF low | P0171 |
| Rich injector leak | STFT/LTFT − | P0172 |
| Misfire | RPM unstable | P0301 |
| Catalyst bad | O2 oscillation | P0420 |
| Overheat | COOLANT high | P0217 |

---

# Quick workflow checklist

```text
1. elm327-emulator -s car -n 35000
2. Define trim_b / maf_h / clt_b helpers at CMD>
3. Apply fault block from this doc
4. test 01xx — confirm hex
5. python obd_connection.py — stream 5+ min, save CSV + label
6. reset — next fault
```

---

# Mapping faults → detector layers

| Layer | What to train |
|-------|----------------|
| Rules | Single-PID thresholds (coolant > 105°C), cross-PID (STFT+ and MAF low) |
| Features | 5-min mean/std/slope per PID |
| XGBoost | Multi-label from session labels in this doc |
| Gemma | Evidence bundle: signature text + live PIDs + optional DTC |

---

## See also

- [pid_definitions.md](pid_definitions.md) — OBD-II PID meanings, units, and encoding
- [fault_profiles.md](fault_profiles.md) — plain-language OBD signatures and simulation concepts (no code)
- [test_commands.md](test_commands.md) — emulator setup, `test` probes, basic overrides
- [emulator_car_queries.md](emulator_car_queries.md) — baseline healthy values for `car`
- [../README.md](../README.md) — pipeline architecture
