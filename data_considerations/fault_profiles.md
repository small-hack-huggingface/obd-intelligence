# Fault profiles (OBD signatures)

Plain-language reference for **how each fault appears on OBD** and **how to simulate it conceptually** in the ELM327-emulator `car` scenario — no emulator code.

For copy-paste override commands and PID encoding, see [fault_simulation.md](fault_simulation.md).

**Prerequisites:** emulator running (`elm327-emulator -s car -n 35000`). See [test_commands.md](test_commands.md) and [emulator_car_queries.md](emulator_car_queries.md).

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

Your detector should learn from **PID patterns over time** (mean, std, slope). DTCs are a bonus layer, not the primary training signal.

---

## How simulation works in the emulator

The emulator normally returns healthy Toyota Auris Hybrid values. To simulate a fault, **override specific PIDs** at the emulator `CMD>` prompt so they return values that match what a real ECU would report.

| Step | What to do |
|------|------------|
| 1 | Choose a fault profile below |
| 2 | Override the listed PIDs to the target values |
| 3 | Confirm with raw hex probes (`test 01xx`) or python-OBD |
| 4 | Stream for **5+ minutes** and label the session |
| 5 | Clear overrides (`reset`) before the next fault |

**Important limitations**

- Overrides are **static** — one set of values per session. Load-dependent faults (weak fuel pump, fan failure) need **separate sessions** (e.g. idle vs cruise).
- Time-varying faults (rising coolant, drifting trims) need **multiple sessions** or manual value changes mid-recording.
- Random variation (misfire, unstable RPM) is simulated by returning a value from a range on each poll.

**PID names** match python-OBD command names: `RPM`, `SPEED`, `COOLANT_TEMP`, `SHORT_FUEL_TRIM_1`, `LONG_FUEL_TRIM_1`, `MAF`, `INTAKE_PRESSURE`, `INTAKE_TEMP`, `ENGINE_LOAD`, `THROTTLE_POS`, `O2_B1S2`, `CONTROL_MODULE_VOLTAGE`, etc. See [emulator_car_queries.md](emulator_car_queries.md) for healthy baselines.

---

## Recording training sessions

After applying a fault profile:

1. **Label** the session in metadata, e.g. `fault=vacuum_leak`, `scenario=idle`.
2. Stream PIDs at ~1 Hz for **5+ minutes** (feature window length).
3. Save timestamp + PID columns to CSV.
4. Clear overrides before the next fault.

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

**Real-world cause:** Unmetered air enters the intake (cracked hose, PCV leak, intake gasket).

**What the ECU sees:** Lean mixture. The ECU adds fuel → positive short- and long-term fuel trim. MAF reads lower than expected for the idle airflow. RPM may sit slightly high at idle.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `SHORT_FUEL_TRIM_1` | Strongly positive (~+20%) |
| `LONG_FUEL_TRIM_1` | Positive (~+15%) |
| `MAF` | Low for idle (~12 g/s) |
| `INTAKE_PRESSURE` | Higher vacuum than normal (~55 kPa absolute at idle) |
| `RPM` | ~950 at idle |
| `SPEED` | 0 km/h |

**How to simulate:** Apply at **idle** (speed 0). Set trims high and positive, MAF low, manifold pressure high, RPM slightly elevated.

**Typical DTC:** `P0171` System Too Lean (Bank 1).

**Detector hint:** Most noticeable at idle — positive trims with low MAF and no load.

---

## 2. Dirty MAF sensor

**Real-world cause:** Contaminated MAF element underestimates airflow.

**What the ECU sees:** Reported airflow is low relative to RPM and engine load. ECU compensates with positive fuel trims.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `RPM` | ~2500 (cruise) |
| `ENGINE_LOAD` | ~50% |
| `MAF` | ~16 g/s (should be ~25 g/s at this RPM/load) |
| `SHORT_FUEL_TRIM_1` | ~+12% |
| `LONG_FUEL_TRIM_1` | ~+10% |
| `SPEED` | ~80 km/h |

**How to simulate:** **Cruise** session — high RPM and load but MAF stuck low, trims compensating.

**Typical DTC:** `P0101` MAF Range/Performance.

---

## 3. Air filter restriction

**Real-world cause:** Blocked filter limits airflow; driver needs more throttle for the same power.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `THROTTLE_POS` | High (~63%) |
| `MAF` | Moderate but low for throttle (~35 g/s) |
| `ENGINE_LOAD` | Low (~27%) at same RPM |
| `RPM` | ~2200 |
| `SPEED` | ~53 km/h |

**How to simulate:** Cruise with high throttle, low MAF, and low load — sluggish acceleration profile. Compare against a healthy cruise session at similar speed.

**Training tip:** Best detected by throttle vs MAF vs speed over time, not a single snapshot.

---

## 4. Stuck open EGR

**Real-world cause:** Exhaust gas enters the intake when it should not.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `COMMANDED_EGR` | 100% (fully open) |
| `RPM` | Unstable idle, jumping ~600–1100 |
| `SHORT_FUEL_TRIM_1` | Mildly positive (~+8%) |
| `SPEED` | 0 km/h |

**How to simulate:** Idle session with EGR commanded fully open and RPM varying randomly each poll.

**Typical DTC:** `P0401` or rough-idle misfire codes when severe.

---

# Fuel system

## 5. Fuel pump weakening

**Real-world cause:** Fuel pressure drops under load; idle may look normal.

**OBD signature**

| Context | Trims | Load |
|---------|-------|------|
| Idle | Normal (~0%) | Low |
| Heavy acceleration | STFT ~+20%, LTFT ~+15% | High load, high RPM |

**How to simulate:** Two **separate sessions** — (A) idle with healthy trims, (B) heavy load with RPM ~4500, speed ~90 km/h, engine load maxed, trims strongly positive.

**Typical DTC:** `P0171` under load; may be intermittent.

---

## 6. Dirty fuel injectors

**Real-world cause:** Reduced spray → uneven combustion.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `SHORT_FUEL_TRIM_1` | ~+14% |
| `LONG_FUEL_TRIM_1` | ~+11% |
| `RPM` | Mild instability ~1100–1350 |

**How to simulate:** Positive trims with slightly unstable RPM at idle or light cruise.

**Typical DTC:** `P0300` random misfire when severe.

---

## 7. Leaking injector

**Real-world cause:** Continuous fuel drip → rich mixture.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `SHORT_FUEL_TRIM_1` | Negative (~−18%) |
| `LONG_FUEL_TRIM_1` | Negative (~−12%) |
| `COMMANDED_EQUIV_RATIO` | Richer than stoichiometric |

**How to simulate:** Strongly **negative** trims (ECU pulling fuel out). Idle or light load.

**Typical DTC:** `P0172` System Too Rich.

---

## 8. Injector stuck closed

**Real-world cause:** One cylinder starved → lean misfire.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `SHORT_FUEL_TRIM_1` | ~+16% |
| `LONG_FUEL_TRIM_1` | ~+8% |
| `RPM` | Unstable ~750–1250 at idle |
| `SPEED` | 0 km/h |

**How to simulate:** Lean positive trims plus erratic idle RPM.

**Typical DTC:** `P0301`–`P0304` cylinder-specific misfire.

---

# Ignition system

## 9. Ignition coil failure

**Real-world cause:** Weak or missing spark on one cylinder.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `RPM` | Large idle swings ~500–1500 |
| `O2_B1S2` | Erratic voltage |
| `SHORT_FUEL_TRIM_1` | Mildly positive |
| `SPEED` | 0 km/h |

**How to simulate:** Random RPM each poll, random downstream O2, idle only.

**Training tip:** High **std** on RPM over 5 minutes at idle is the strongest feature.

**Typical DTC:** `P0301` (cylinder 1 misfire).

---

## 10. Spark plug wear

**Real-world cause:** Gradual loss of ignition efficiency.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `LONG_FUEL_TRIM_1` | Slowly increasing over weeks/sessions (+4% → +9% → +14%) |
| `SHORT_FUEL_TRIM_1` | Follows LTFT upward |

**How to simulate:** Three labeled sessions with escalating LTFT: early (+4%), mid (+9%), late (+14%).

**Training tip:** Model learns **positive slope** on LTFT across sessions.

---

# Cooling system

## 11. Thermostat stuck open

**Real-world cause:** Coolant bypasses the radiator; engine never fully warms up.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `COOLANT_TEMP` | ~65°C after long run (expect ~90°C) |
| `RUN_TIME` | High (engine has been running a long time) |

**How to simulate:** Coolant stuck low while run time indicates the engine has been on for 15+ minutes.

**Typical DTC:** `P0128` Coolant Thermostat.

**Detector hint:** Engine not reaching operating temperature despite extended runtime.

---

## 12. Thermostat stuck closed

**Real-world cause:** Coolant cannot circulate → rapid overheating.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `COOLANT_TEMP` | Rising: 85°C → 95°C → 105°C → 112°C |
| `SPEED` | Moderate (~25 km/h) or idle |

**How to simulate:** Record **multiple short sessions** at increasing coolant values, or change the override every ~2 minutes while streaming to build a temperature **slope** feature.

**Typical DTC:** `P0217` Engine Coolant Over Temperature.

---

## 13. Cooling fan failure

**Real-world cause:** No airflow at standstill; fine when moving.

**OBD signature**

| Session | `SPEED` | `COOLANT_TEMP` |
|---------|---------|----------------|
| Moving (healthy fan not needed) | ~60 km/h | ~88°C |
| Idle / traffic | 0 km/h | ~108°C |

**How to simulate:** Two sessions — cruise with normal temp, then idle with high coolant and low RPM (~750).

**Training tip:** High coolant **only when** speed mean is near zero.

---

## 14. Water pump degradation

**Real-world cause:** Reduced circulation; overheating under load.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `RPM` | ~3800 |
| `ENGINE_LOAD` | High (~75%) |
| `COOLANT_TEMP` | ~102°C (elevated under load) |

**How to simulate:** High-load session with elevated coolant. Pair with a healthy baseline at the same RPM/load (~88°C).

---

## 15. Low coolant

**Real-world cause:** Air pockets and intermittent circulation → unstable temperature.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `COOLANT_TEMP` | Jumps around ~77–110°C (random each poll) |

**How to simulate:** Coolant varying randomly within a wide band at idle or light load.

**Training tip:** High **std** on coolant distinguishes this from thermostat stuck closed (steady rising slope).

---

# Emissions system

## 16. Catalytic converter degradation

**Real-world cause:** Catalyst loses efficiency; downstream O2 should stay flat but starts oscillating like upstream.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `O2_B1S2` | Oscillating (random ~0.15–0.85 V each poll) |
| `O2_S1_WR_VOLTAGE` | Oscillating upstream |

**Healthy baseline:** Downstream O2 steady ~0.4 V.

**How to simulate:** Fault session with both O2 sensors varying randomly. Compare against healthy session with flat downstream O2.

**Typical DTC:** `P0420` Catalyst Efficiency Below Threshold.

---

## 17. Catalytic converter restriction

**Real-world cause:** Clogged catalyst → backpressure, low power.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `ENGINE_LOAD` | High demand (~94%) |
| `MAF` | Low (~28 g/s) for the load |
| `RPM` | ~2800 |
| `SPEED` | ~64 km/h (sluggish) |
| `CATALYST_TEMP_B1S1` | Elevated |

**How to simulate:** High load and throttle demand but poor speed/MAF — feels like driving with the brakes on.

**Typical DTC:** `P0420` / power-loss complaints.

---

## 18. EVAP purge valve stuck open

**Real-world cause:** Fuel vapors enter intake at the wrong time (especially after refueling).

**OBD signature**

| PID | Pattern |
|-----|---------|
| `EVAPORATIVE_PURGE` | 100% open |
| `SHORT_FUEL_TRIM_1` | ~+14% |
| `LONG_FUEL_TRIM_1` | ~+6% |
| `SPEED` | 0 km/h (idle) |

**How to simulate:** Idle with purge fully commanded and positive trims.

**Typical DTC:** `P0441` EVAP Incorrect Purge Flow.

---

# Sensors

## 19. O2 sensor drift

**Real-world cause:** Aging sensor; trims drift without a clear mechanical fault.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `LONG_FUEL_TRIM_1` | Slowly increasing across sessions (+6% → +10% → +14%) |
| `O2_B1S2` | Sluggish, small variation around mid voltage |

**How to simulate:** Mild positive LTFT with O2 barely moving. Escalate LTFT across multiple sessions.

**Typical DTC:** `P0136` O2 Circuit (B1S2) when severe.

---

## 20. O2 sensor failure

**Real-world cause:** Sensor dead — flatlined output.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `O2_B1S2` | Stuck at 0 V **or** stuck at ~1.0 V continuously |

**How to simulate:** Two variants — stuck low session and stuck high session.

**Training tip:** O2 **std ≈ 0** over 5 minutes is the tell.

---

## 21. Intake air temperature sensor failure

**Real-world cause:** IAT reading implausible.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `INTAKE_TEMP` | Stuck at −40°C **or** stuck at ~120°C |

**How to simulate:** One session per stuck value. Real IAT should track ambient and warm slightly after driving.

**Typical DTC:** `P0112` / `P0113` IAT Circuit Low/High.

---

## 22. Coolant temperature sensor failure

**Real-world cause:** ECT reads cold when engine is warm → ECU runs rich.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `COOLANT_TEMP` | −40°C (impossible when running) |
| `SHORT_FUEL_TRIM_1` | Negative (~−10%) from over-fueling |

**How to simulate:** Coolant stuck at minimum while engine is clearly running (high RPM or long run time).

**Typical DTC:** `P0117` ECT Circuit Low.

---

## 23. MAP sensor failure

**Real-world cause:** Manifold pressure inconsistent with RPM, throttle, and MAF.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `RPM` | ~3000 |
| `THROTTLE_POS` | ~44% |
| `INTAKE_PRESSURE` | ~95 kPa (reads like idle vacuum at high RPM) |
| `MAF` | ~45 g/s (normal for RPM — mismatch with MAP) |

**How to simulate:** High RPM and MAF but MAP still showing idle-level vacuum.

**Typical DTC:** `P0106` MAP Performance.

---

## 24. Throttle position sensor failure

**Real-world cause:** Throttle reading stuck while engine speed changes.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `THROTTLE_POS` | Stuck ~12% |
| `RPM` | Varying ~900–2500 |

**How to simulate:** Fixed throttle PID with changing RPM.

**Typical DTC:** `P0122` / `P0123` TPS Circuit.

---

# Electrical system

## 25. Alternator failure

**Real-world cause:** Charging system cannot maintain voltage.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `CONTROL_MODULE_VOLTAGE` | Falling: 14.4 → 13.8 → 13.1 → 12.7 V while running |
| `RPM` | ~1100 (engine running) |

**How to simulate:** Separate sessions at each voltage step to train a **descending voltage slope**.

**Typical DTC:** `P0562` System Voltage Low.

---

## 26. Weak battery

**Real-world cause:** Battery cannot hold charge; voltage drops over time key-on.

**OBD signature**

| Condition | Pattern |
|-----------|---------|
| Engine off / key on | Supply trend 12.6 → 12.3 → 11.9 V |

**How to simulate:** Marginal adapter supply ~11.9 V. Note: `CONTROL_MODULE_VOLTAGE` with engine running reflects the alternator more than the battery.

**Training tip:** Trend across key-on events; harder to simulate fully on the emulator alone.

---

## 27. Voltage regulator failure

**Real-world cause:** Overcharging.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `CONTROL_MODULE_VOLTAGE` | ~15.8 V while running |

**How to simulate:** Single session with module voltage well above normal (~14.4 V).

**Typical DTC:** `P0563` System Voltage High.

---

# Mechanical engine

## 28. Engine compression loss

**Real-world cause:** Ring or valve wear — OBD only shows indirect signs.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `RPM` | Unstable ~700–1300 |
| `ENGINE_LOAD` | Low (~19%) despite high throttle |
| `THROTTLE_POS` | High (~75%) |
| `MAF` | Low (~22 g/s) |
| `SHORT_FUEL_TRIM_1` | ~+10% |

**How to simulate:** High throttle demand, low load and MAF, unstable RPM — weak power with compensation trims.

**Difficulty:** Hard — combine multiple weak signals; label as advanced class.

---

## 29. Head gasket leak

**Real-world cause:** Combustion gas enters coolant; misfire and overheating together.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `COOLANT_TEMP` | Unstable ~95–115°C |
| `RPM` | Erratic ~650–1200 |
| `SHORT_FUEL_TRIM_1` | ~+8% |

**How to simulate:** Combine unstable coolant, misfire-like RPM, and mild positive trim in one idle session.

**Typical DTC:** `P0300` plus overheating codes. Real diagnosis often needs exhaust gas in coolant (not visible on standard OBD).

---

## 30. Timing chain stretch

**Real-world cause:** Valve timing drifts; subtle performance and economy loss.

**OBD signature**

| PID | Pattern |
|-----|---------|
| `TIMING_ADVANCE` | Low (~12° vs normal ~20°+) |
| `LONG_FUEL_TRIM_1` | ~+7% |
| `ENGINE_LOAD` | ~33% at cruise |
| `RPM` | ~2400 |
| `SPEED` | ~85 km/h |

**How to simulate:** Cruise session with retarded timing and mildly elevated LTFT. Compare against healthy baseline at same speed/RPM.

**Difficulty:** Hard — best for LLM reasoning or low-confidence detector class.

---

# Transmission / drivetrain

Standard OBD-II on the `car` scenario exposes **limited** transmission data. Proxy symptoms only:

| Symptom | What to simulate |
|---------|------------------|
| Slipping (high RPM, low speed) | RPM ~4200, speed ~25 km/h, moderate load |
| Converter shudder | RPM oscillating at steady speed |

**Note:** Real transmission diagnosis usually needs manufacturer-specific PIDs not in the 86-command `car` list.

---

# Optional: DTC pairing

For v1 training, **PID signatures are enough**. When you want DTC testing, pair live PID faults with stored codes:

| Fault | Live PID pattern | Typical DTC |
|-------|------------------|-------------|
| Vacuum leak | STFT/LTFT +, MAF low | P0171 |
| Rich injector leak | STFT/LTFT − | P0172 |
| Misfire | RPM unstable | P0301 |
| Catalyst bad | O2 oscillation | P0420 |
| Overheat | COOLANT high | P0217 |

See [test_commands.md](test_commands.md) for DTC override options. Code meanings: [toyota_dtc_definitions.md](toyota_dtc_definitions.md).

---

# Mapping faults → detector layers

| Layer | What to train |
|-------|----------------|
| Rules | Single-PID thresholds (coolant > 105°C), cross-PID (STFT+ and MAF low) |
| Features | 5-min mean / std / slope per PID |
| XGBoost | Multi-label from session labels in this doc |
| Gemma | Evidence bundle: signature text + live PIDs + optional DTC |

---

## See also

- [pid_definitions.md](pid_definitions.md) — OBD-II PID meanings and encoding
- [fault_simulation.md](fault_simulation.md) — emulator override commands and PID encoding
- [test_commands.md](test_commands.md) — emulator setup and hex probes
- [emulator_car_queries.md](emulator_car_queries.md) — baseline healthy values for `car`
- [../README.md](../README.md) — pipeline architecture
