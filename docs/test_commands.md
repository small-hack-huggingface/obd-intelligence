# Test commands

How to test the OBD pipeline against the ELM327 emulator. Always use two terminals.

**Environment:** `conda activate small-hack-1`

---

## 1. Start the emulator (Terminal 1)

```powershell
elm327-emulator -s car -n 35000
```

| Flag | Meaning |
|------|---------|
| `-s car` | Toyota Auris Hybrid scenario (86 supported PIDs) |
| `-n 35000` | Listen on TCP port 35000 |

Leave this window open. You should see `CMD>`.

Other scenarios (type at `CMD>` or use `-s <name>` on startup):

| Scenario | Command | What it does |
|----------|---------|--------------|
| `car` | `scenario car` | Ignition on, full PID set |
| `engineoff` | `scenario engineoff` | Ignition off, no OBD data |
| `default` | `scenario default` | Generic ECU responses |
| `mt05` | `scenario mt05` | Delphi MT05 ECU (motorbike/ATV) |

---

## 2. Python tests (Terminal 2)

From the repo root (script lives in `scratch_code/`):

```powershell
conda activate small-hack-1
cd C:\Users\dsouz\small-hack
pip install -r requirements.txt
```

### Smoke test -- connect and stream

```powershell
cd scratch_code
python obd_connection.py
```

Connects to `socket://localhost:35000`, prints one sample, then 10 samples at ~1 Hz.

**Expect:** `Status: Car Connected` and RPM/SPEED/COOLANT_TEMP values.

### Discover all supported queries

```powershell
cd scratch_code
python obd_connection.py --discover
```

Queries all 86 commands the `car` scenario supports and prints sample values.

Full output table: [emulator_car_queries.md](emulator_car_queries.md)

### One-liner -- single PID

```powershell
cd scratch_code
python -c "from obd_connection import connect; import obd; c=connect(); print(c.query(obd.commands.RPM).value); c.close()"
```

### One-liner -- trouble codes

```powershell
cd scratch_code
python -c "from obd_connection import connect; import obd; c=connect(); print(c.query(obd.commands.GET_DTC).value); c.close()"
```

**Expect on clean emulator:** `[]` (no codes).

### Custom port

```powershell
set OBD_PORT=socket://localhost:35000
cd scratch_code
python obd_connection.py
```

---

## 3. Emulator `CMD>` commands (Terminal 1)

Type these at the `CMD>` prompt while the emulator is running.

### Probe raw PID responses -- why each one matters

Use `test <hex>` at the `CMD>` prompt to ask the **fake ECU one question** and see the raw hex answer -- without running Python. Format: no spaces (`test 010c`, not `test 01 0c`).

**Why use `test` at all?**

| You want to... | Use `test` in emulator | Use Python |
|----------------|------------------------|------------|
| Check the fake car responds | Yes -- instant, no code | Overkill |
| Debug a single PID in isolation | Yes | Also works |
| Build the real streaming pipeline | No | Yes -- this is production path |
| Feed XGBoost / Gemma | No | Yes -- needs decoded values over time |

Run `test` commands **while building** to confirm the emulator works. Run **Python** to confirm your app works.

---

#### `test 010c` -- RPM

**Purpose:** Verify the engine-speed channel works end-to-end.

**Why we need it:** RPM is the #1 input for misfire detection. Your feature extractor computes mean/std/slope on RPM over 5 minutes; XGBoost uses those patterns to flag `{misfire: 0.78}`. If RPM does not respond here, the whole downstream pipeline has nothing to learn from.

**When to run:** First test after starting the emulator. Re-run after `scenario engineoff` / `scenario car` or after overriding `emulator.answer['RPM']`.

---

#### `test 010d` -- Vehicle speed

**Purpose:** Confirm the ECU reports motion separately from engine speed.

**Why we need it:** Speed + RPM together tell idle vs driving apart. A misfire at idle looks different from one under load. Your stream polls SPEED alongside RPM so the model does not confuse "high RPM, zero speed" (neutral revving) with "driving".

**When to run:** After RPM works. Compare with Python `obd.commands.SPEED`.

---

#### `test 0105` -- Coolant temperature

**Purpose:** Check the thermal sensor path is alive.

**Why we need it:** Overheating is a distinct fault class from misfire. Coolant temp trend (slope over 5 min) can trigger Gemma even when XGBoost has no trained class yet -- "coolant climbing past 100 C" is explainable without ML.

**When to run:** When testing overheating scenarios (override `COOLANT_TEMP` in emulator).

---

#### `test 0104` -- Engine load

**Purpose:** Verify the ECU reports how hard the engine is working.

**Why we need it:** Load contextualizes RPM and MAF. High load + erratic RPM strengthens a misfire signal; high load + normal RPM weakens it. Included in your default `PIDS` list in `obd_connection.py`.

**When to run:** When tuning feature windows -- load should move when you override RPM/MAF together.

---

#### `test 0110` -- Mass air flow (MAF)

**Purpose:** Confirm airflow measurement reaches the host.

**Why we need it:** Vacuum leaks and MAF failures show up here before RPM becomes unstable. MAF vs RPM mismatch is a strong feature for lean-condition / vacuum-leak labels in XGBoost.

**When to run:** When simulating vacuum-leak patterns (high MAF at idle with positive fuel trim).

---

#### `test 0106` -- Short-term fuel trim (bank 1)

**Purpose:** Check immediate fuel correction data is available.

**Why we need it:** STFT reacts in seconds. Spikes here feed the slope feature -- a trim drifting positive over 5 minutes suggests lean running even if RPM looks fine.

**When to run:** Fuel-system fault testing alongside `test 0107`.

---

#### `test 0107` -- Long-term fuel trim (bank 1)

**Purpose:** Check learned fuel correction data is available.

**Why we need it:** LTFT confirms chronic problems STFT only catches briefly. Pair with STFT: both positive = sustained lean (vacuum leak, weak pump); both negative = sustained rich.

**When to run:** When building training labels for fuel-system faults.

---

#### `test 010b` -- Intake manifold pressure

**Purpose:** Verify vacuum / boost pressure reads correctly.

**Why we need it:** At idle this is engine vacuum. Weak vacuum + high MAF + positive trim = classic vacuum-leak signature your model should learn.

**When to run:** Vacuum-leak simulation testing.

---

#### `test 010f` -- Intake air temperature

**Purpose:** Confirm ambient air temp sensor path works.

**Why we need it:** IAT validates that other readings make sense (air density). Less critical for v1 misfire detection, but useful context for Gemma explanations ("IAT matches ambient, so lean condition is not heat-related").

**When to run:** Optional sanity check; lower priority than RPM/MAF/trim.

---

#### Summary -- which PIDs feed which pipeline stage

```
test 010c/010d/0104/0110/0106/0107/010b/0105/010f
        |
        v
  python-OBD stream (~1 Hz)     <-- obd_connection.py / future stream.py
        |
        v
  5-min window: mean, std, slope  <-- feature extractor
        |
        v
  XGBoost fault probabilities     <-- misfire, vacuum_leak, ...
        |
        v
  Gemma explanation               <-- plain-language "what's wrong"
```

| Command | Primary fault context | In default stream? |
|---------|----------------------|-------------------|
| `test 010c` | Misfire | Yes |
| `test 010d` | Context (idle vs drive) | Yes |
| `test 0105` | Overheating | Yes |
| `test 0104` | Load / misfire context | Yes |
| `test 0110` | Vacuum leak, MAF fault | Yes |
| `test 0106` | Lean / rich (immediate) | Yes |
| `test 0107` | Lean / rich (chronic) | Yes |
| `test 010b` | Vacuum leak | Yes |
| `test 010f` | Sensor / ambient context | Yes |

After a `test` passes, confirm Python sees the same PID:

```powershell
cd scratch_code
python -c "from obd_connection import connect; import obd; c=connect(); print('RPM:', c.query(obd.commands.RPM).value); c.close()"
```

### Monitor and debug

| Command | What it does |
|---------|--------------|
| `counters` | Show how many times each PID was queried |
| `reset` | Clear counters and emulator state |
| `help` | List available emulator commands |
| `port` | Show TCP port (should be 35000) |
| `quit` | Stop the emulator |

### Switch vehicle state

```
scenario car
scenario engineoff
scenario default
```

After `engineoff`, retry Python -- expect connection failure or no data.

---

## 4. Simulate faults (Terminal 1 `CMD>`)

Use these to test how your app handles bad readings.

### Force RPM to 500

```python
emulator.answer['RPM'] = '<exec>ECU_R_ADDR_E + " 04 41 0C %.4X" % int(4 * 500)</exec><writeln />'
```

Then in Terminal 2, query RPM again.

### Force speed sensor dropout

```python
emulator.answer['SPEED'] = '<writeln>NO DATA</writeln>'
```

Tests null handling in your stream code.

### Restore default answer for a PID

```python
del emulator.answer['RPM']
```

Or reset everything:

```
reset
```

---

## 5. Test scenarios (step by step)

### A. Connection smoke test

1. Terminal 1: `elm327-emulator -s car -n 35000`
2. Terminal 2: `cd scratch_code` then `python obd_connection.py`
3. **Pass if:** `Car Connected` and numeric PID values print

### B. Full PID inventory

1. Emulator running
2. `cd scratch_code` then `python obd_connection.py --discover`
3. **Pass if:** 86 commands listed with sample values

### C. Raw emulator probe

1. At `CMD>`: `test 010c`
2. **Pass if:** hex response like `41 0C ...` (RPM data)

### D. Ignition off

1. At `CMD>`: `scenario engineoff`
2. Terminal 2: run `obd_connection.py` again
3. **Pass if:** connection fails or returns no useful data
4. Restore: `scenario car`

### E. Sensor override (misfire-like)

1. At `CMD>`: set `emulator.answer['RPM']` to a fixed low value (see section 4)
2. Stream with `obd_connection.py`
3. **Pass if:** Python shows the overridden RPM
4. Restore: `del emulator.answer['RPM']`

### F. Sensor dropout

1. At `CMD>`: force SPEED to `NO DATA` (see section 4)
2. Stream and check your code handles `None`
3. Restore: `del emulator.answer['SPEED']`

### G. Feature window dev (~1 Hz stream)

1. Emulator running, scenario `car`
2. Run `obd_connection.py` (10 samples) or extend the loop
3. **Use for:** building the 5-minute mean/std/slope extractor

### H. Freeze frame vs live

1. `--discover` and compare `RPM` vs `DTC_RPM` values
2. **Use for:** LLM context when a DTC is set (future)

### I. Clean DTC baseline

1. `python -c "... GET_DTC ..."` (see section 2)
2. **Expect:** `[]` on the emulator's clean car

### J. Traffic audit

1. Run Python stream for a while
2. At `CMD>`: `counters`
3. **See which** PIDs python-OBD actually queried

---

## 6. Troubleshooting

| Problem | Fix |
|---------|-----|
| `Connection refused` | Start emulator first (`-n 35000`) |
| `Not Connected` | Check port matches; try `scenario car` |
| `Invalid request: '\x7f\x7f'` in emulator log | Normal on connect; `obd_connection.py` uses `baudrate=38400` to avoid this |
| `ModuleNotFoundError: obd` | `conda activate small-hack-1` then `pip install obd` |
| Garbled README in editor | Re-open file; ensure encoding is UTF-8 |

---

## See also

- [fault_simulation.md](fault_simulation.md) -- 30 fault profiles with copy-paste emulator overrides
- [emulator_car_queries.md](emulator_car_queries.md) -- all 86 queries with sample values
- [../README.md](../README.md) -- project overview and architecture
