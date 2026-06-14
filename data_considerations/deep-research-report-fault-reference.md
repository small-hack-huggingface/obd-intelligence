# Automotive OBD-II PIDs & Fault Reference

**Executive Summary:** This reference sheet explains key OBD-II parameter IDs (PIDs) – what they measure, normal ranges, failure modes – and how they change under common faults (lean/rich fuel mixtures, sensor failures, mechanical issues, etc.). It then summarizes 31 simulated fault profiles (e.g. vacuum leak, dirty MAF, ignition misfires, cooling problems, etc.), highlighting their signature scan-tool readings, likely causes, and step-by-step diagnostic actions. Tables map each fault to its symptoms, causes, and recommended next steps. Practical tips on live-data interpretation, test procedures, and safety are also provided. 

## Key PID Definitions & Normal Ranges

- **Engine RPM:** Crankshaft speed in revolutions per minute. Normal idle ~700–900 rpm; WOT (wide-open throttle) ~3000–4000 rpm or higher.  
- **Vehicle Speed:** Road speed (km/h or mph) from wheel/transmission sensors. Zero at idle, increases with throttle.  
- **Calculated Engine Load:** Normalized engine load (%) based on airflow (percent of max torque). ~30–50% at idle on NA engines; reaches 100% at WOT. Calculated from MAP, MAF and barometer.  
- **Intake Manifold Pressure (MAP, kPa or inHg):** Pressure in intake manifold. At idle, high vacuum (~20–30 inHg); at WOT it approaches atmospheric (0–10 inHg vacuum). PCM uses MAP for load and fueling. A stuck-open throttle or vacuum leak skews MAP (higher than expected vacuum).  
- **Mass Air Flow (MAF, g/s or lb/min):** Air mass entering engine. Idle ~2–7 g/s; at moderate cruising (~2500 rpm) ~15–25 g/s. Dirty or failing MAF gives **lower** readings for a given RPM. Check MAF accuracy with a scan tool or meter, compare against known specs.  
- **Intake Air Temp (IAT, °C/°F):** Air temperature entering engine. Normal ~ ambient. Implausible IAT (e.g. –40°C) means sensor shorted. A stuck-cold IAT makes PCM over-fuel (rich trim).  
- **Engine Coolant Temp (ECT, °C/°F):** Coolant/engine temp. Should warm up to ~90–100°C (190–212°F). Stuck-open thermostat yields ~60–70°C after warm-up (long run time). Stuck-closed thermostat yields ~110°C (overheat).  
- **Throttle Position (TPS, %):** Throttle plate angle (0% closed, 100% wide open). Correlates with engine load. Stuck TPS (e.g. locked at ~12%) shows no change with pedal movement.  
- **Oxygen Sensors (O₂ B1S1/2, V or λ):** Measure exhaust O₂. Bank1 Sensor1 (upstream pre-cat) swings 0.1–0.9 V as mixture oscillates; B1S2 (downstream) should be steady ~0.4–0.6 V when cat is good. Wideband “WR” (voltage or λ) sensors output a linear voltage or ratio ~0.0–5.0 V (some scanners label this). Fault: O₂ stuck high/low means sensor dead; upstream and downstream sensors tracking suggests a bad catalytic converter.  
- **Short-Term Fuel Trim (STFT, Bank1):** Immediate fuel correction (%). Normal ~–10% to +10%. *Positive* STFT (e.g. +10–+20%) = PCM adding fuel to fix a lean condition. *Negative* STFT means removing fuel (rich condition).  
- **Long-Term Fuel Trim (LTFT, Bank1):** Averaged (long-term) fuel correction. Should return near 0% at steady state, but ±5–8% is common. LTFT beyond ±10% indicates a persistent issue.  
- **Catalyst Temp (B1S1, °C):** Exhaust gas temperature at catalytic converter inlet (via sensor in B1S1). Typical idle temps ~300–600°C, at full load can exceed 800°C. High temp at constant RPM/gear indicates a clogged catalyst. (OBD PID 0x3C; -40 offset).  
- **Ignition Timing Advance (Spark Adv, °):** Timing in degrees before TDC. Typically 10–30° at idle, up to ~40° under light cruise. Retarded/low advance (e.g. 0°–10° at cruise) suggests timing-chain/chain-stretch or cam/crank sync issue.  
- **Control Module Voltage (Battery, V):** Vehicle electrical system voltage (0–65.535 V range). Normal ~13.8–14.5 V when charging. ~12.7 V running = weak alternator; ≥15.5 V = overcharging/regulator fault.  
- **EVAP Purge Command (%):** Purge valve duty (0% off, 100% on). Normally 0% at idle; if stuck at 100% at idle, PCM floods intake with fuel vapor (lean idle lean mixture).  
- **EGR Command (%):** EGR valve duty (0% closed, 100% fully open). Normally 0% at idle and low load; if stuck at 100%, large EGR flow causes misfire/rough idle.

_Normal Ranges:_ STFT/LTFT typically ±10% (see above). Normal idle RPM ~750 ±100. Normal coolant ~90°C (190°F). O₂ voltage oscillates ~0.1–0.9 V quickly in closed-loop. Normal IAT ~ambient. MAF varies by engine size (see above).  

**How Measured:** The PCM reads sensors (thermistors, pressure sensors, Hall/crank sensors, etc.) and reports via OBD-II PIDs. For example, MAF often uses a hot-wire or hot-film sensor output (g/s); MAP uses a piezo or silicon sensor (kPa); TPS often a potentiometer (voltage). Engine load is calculated from MAP/MAF. O₂ sensors (zirconia or wideband) output voltage or current proportional to O₂ content.  

**Common Failure Modes:** 
- *Fuel Trim Issues:* Caused by vacuum leaks, MAF faults, fuel system problems, injector issues, or oxygen sensor faults. 
- *MAF Sensor:* Dirty/contaminated element, wiring short, or inlet leak (unmetered air) gives low readings.
- *MAP Sensor:* Vacuum line blockage or sensor failure causes incorrect load reading. 
- *TPS:* Wear or misalignment yields erratic or fixed throttle readings. 
- *O₂ Sensors:* Aging sensor slows or sticks. A dead zirconia sensor reports flat (0 V) or pegged high (0.9 V). 
- *Coolant/IAT Sensors:* Short/open circuits show –40°C (code 0x00). 
- *Purge/EGR:* Stuck solenoids or valves cause stuck 0%/100% commands. 
- *Catalyst:* Clogging raises upstream temperature; a dead cat lets downstream O₂ mimic upstream. 
- *Voltage:* Bad alternator or regulator yields out-of-range voltage.

Each PID’s **fault symptom** on live data often correlates to these: e.g. lean (vacuum leak) → STFT↑, MAF↓, idle↑; rich (injector leak) → STFT↓ (negative); O₂ stuck → flat-line voltage; EGR stuck → EGR% 100%, RPM bouncing; etc.

## Recurring PID Themes

These are common patterns seen in multiple faults:

- **Lean Compensation:** STFT/LTFT **positive** (often +6% to +20%) – PCM adding fuel. Indicates a lean mixture (vacuum leak, low fuel, clogged filter, dirty MAF, etc.). Idle may be high (1500+ rpm) if too much unmetered air. 
- **Rich Compensation:** STFT/LTFT **negative** (e.g. –10% to –18%) – PCM removing fuel. Causes: leaking injector, high fuel pressure, faulty fuel pressure regulator, stuck-rich sensor. 
- **Low MAF Readings:** MAF (g/s) abnormally **low** for given RPM/load (e.g. 12–22 g/s when more expected). Root: dirty/failed MAF, air bypass (intake leak, hole). Check linearity by graphing MAF vs RPM. 
- **High Throttle, Low Output:** Throttle position high (e.g. 60–75%), but engine load (MAF, Torque) low. Often from low compression (one cylinder misfire) or mechanical drag. Check compression test and ignition. 
- **Unmetered Air / Vacuum Leak:** Idle lean: STFT/LTFT jumps high, MAF low, intake pressure ~high vacuum, idle RPM ~500–1500. Classic pattern: pronounced high trims + high idle. Confirm with smoke test or by covering vacuum ports.  
- **Load-only Lean:** Normal trims at idle but STFT ~+20%, LTFT +15% under high load (full throttle). Possible weak fuel pump or injector; fuel pressure drops under demand. Check fuel pressure, pump flow. 
- **Idle Instability:** RPM bouncing 500–1500, O₂B1S2 oscillating. Likely misfire or severe vacuum leak. Check misfire counters (DTC P030x), ignition coils, plug wires, and vacuum lines. 
- **EGR Stuck Open:** Commanded EGR 100% (flat), unstable/higher idle, mild positive trim. Root cause: EGR valve or solenoid stuck. Test by applying vacuum/power to EGR and listening.  
- **EVAP Purge Stuck:** EVAP purge command 100% at idle, with positive fuel trims (lean idle). Means purge solenoid stuck open dumping fuel vapor. Check by disabling purge valve (unplug coil) and watching idle. 
- **Coolant Too Cold:** ECT ~60–70°C after long run time, LTFT lean (PCM enriching for perceived cold). Likely stuck-open thermostat or low coolant. 
- **Overheating:** Coolant ≥102–112°C. Potential thermostat stuck closed, fan fault, or coolant level. At idle (speed 0) exclusive: fan relay or sensor issue. 
- **Unstable Coolant:** ECT fluctuates wildly 77–110°C. Air pocket or failing sensor. Check gauge vs scanner, bleed system. 
- **O₂ Oscillating (Bad Cat):** O₂ B1S2 (downstream) oscillates (voltage swings) nearly matching upstream O₂S1. Indicates cat not absorbing O₂ (degraded). 
- **O₂ Stuck:** B1S2 flat 0 V or pegged high (0.9 V). Indicates open/shorted O₂ sensor circuit. 
- **O₂ Drift:** Downstream flat around mid-level ± small swing; LTFT slowly increases. Cat likely working but upstream or fueling is drifting lean. Replace O₂ or check mixture. 
- **IAT Implausible:** IAT reads –40°C (0x00). Sensor open/short. Results in rich trim (PCM thinks very cold air). 
- **ECT Sensor Dead:** ECT –40°C, rich STFT (–10%). False cold reading causes over-rich compensation. 
- **MAP Mismatch:** High RPM (~3000) + moderate throttle, but MAP reading stays like idle (high vacuum). Could be MAP sensor fault or shorted vacuum line.  
- **TPS Stuck:** TPS fixed (~12%) while RPM varies. Pedal and RPM decoupled. Swap or calibrate TPS. 
- **Low Battery Voltage:** Control module ~12.7 V during run. Weak alternator/battery.  
- **High Voltage:** ~15.8 V on run. Overcharging/regulator stuck.  
- **Catalyst Restriction:** High engine load (e.g. 90%), low MAF flow, normal RPM/speed, **Cat Temp rising**. Choked exhaust. Measure backpressure or inspect cat. 
- **Timing Off:** Timing advance abnormally low (e.g. 0–10° at cruise), LTFT +. Late timing causes poor power. Likely cam/crank sync. Use timing light or scan cam/crank sync. 
- **RPM vs Speed Mismatch:** RPM high (4000+) but vehicle speed low (~25 km/h) at moderate load. Indicates transmission slipping or torque converter lock-up failure.

## Fault Profiles & Diagnostics

Below are the 31 simulated fault signatures with diagnostics:

| **Fault**                  | **Key PIDs** (overridden values)                           | **Likely Causes**                           | **Diagnostic Steps**                                                                                      | **Action**                             |
|----------------------------|------------------------------------------------------------|---------------------------------------------|-----------------------------------------------------------------------------------------------------------|----------------------------------------|
| **vacuum_leak**            | STFT +20%, LTFT +15%, MAF 12 g/s, Intake Pressure low, RPM 950, Speed 0 | Intake vacuum leak (hose, gasket), unmetered air | Listen/pressure-test intake for leaks; smoke-test system; block off hoses to isolate; check MAF (cover air tube). Expect idle drop when large leak closed. | Seal leak, retest trims.               |
| **dirty_maf**              | RPM 2500, Load ~50%, MAF 16 g/s, STFT +12%, LTFT +10%, Speed ~50 km/h | Contaminated MAF element, wrong airflow | Inspect/clean MAF sensor with cleaner; compare MAF vs RPM (should rise linearly). Swap in known-good. | Replace/clean MAF if out of spec.      |
| **air_filter_restriction** | Throttle ~63%, MAF 35 g/s, Load ~27%, RPM 2200, Speed ~35 km/h   | Severe intake restriction (blocked filter)  | Inspect air filter; measure MAF vs throttle. Filter clogged yields high throttle% for low airflow.   | Replace air filter.                    |
| **egr_stuck_open**         | Commanded EGR 100%, RPM fluctuating 600–1100, STFT +8%, Speed 0   | EGR valve/solenoid stuck open              | With engine off, measure vacuum/power on EGR – should move plate. At idle, suck on EGR vacuum line: engine should stumble. | Fix/replace EGR valve; clear codes.    |
| **fuel_pump_weak_load**    | (Normal idle), but under load: RPM 4500, Speed 90 km/h, STFT +20%, LTFT +15% | Low fuel pressure under demand            | Perform fuel pressure test at idle and under WOT. Check pump flow. Under load trimming lean = pump or filter. | Replace fuel pump/filter.             |
| **dirty_injectors**        | STFT +14%, LTFT +11%, RPM wobble 1100–1350 (misfire feel)      | Clogged injectors, poor spray pattern      | Check scan misfire counters; swap injectors cylinder-to-cylinder – misfire should follow. Ultrasonic clean injectors. | Clean or replace injectors.           |
| **injector_leak**          | STFT −18%, LTFT −12% (rich trims)                           | Leaking injector(s)                        | Idle fuel pressure test (bleed). Cylinder balance test: introduce known vacuum leak to see cylinder output; leak injector overflows. | Replace leaking injector.             |
| **injector_stuck_closed**  | STFT +16%, LTFT +8%, RPM 750–1250 (idle hunt), Speed 0        | Injector stuck shut (fuel starvation)      | Scan for misfire on specific cylinder; swap injector or connector. Bypass injector control and gauge output. | Replace failed injector.             |
| **ignition_coil_failure**  | RPM 500–1500 random, O₂ B1S2 random swing, STFT +6%, Speed 0   | Failed coil (misfire on one or more cylinders) | Use a spark tester or oscilloscope to verify coil output. Swap coil to new cylinder to see if misfire follows.   | Replace faulty coil; check plugs.     |
| **spark_plug_wear**        | LTFT +9%, STFT +6% (slow rise, no RPM noise)                | Aged plugs, increased gap                 | Inspect spark plugs for wear/gapping. Check spark intensity. On-spark test at idle vs baseline.    | Replace spark plugs.                   |
| **thermostat_stuck_open**  | ECT ~65°C after long run time (0x0E10 sec), >> Low temp    | Thermostat failed open                    | Verify with IR thermometer or scan tool: block heater to warm to ~90°C; if never reached, suspect thermostat. | Replace thermostat.                  |
| **thermostat_stuck_closed**| Coolant 112°C at speed ~25 km/h (overheat in motion)       | Thermostat failed closed                  | Monitor ECT while running; if rising uncontrolled, check hoses for heat. Feel upper hose (cold = stuck closed). | Replace thermostat; flush if needed.  |
| **cooling_fan_failure_idle**| Coolant 108°C at speed 0, RPM 750 (idle overheat only)   | Electric fan not running at idle           | With engine hot (~100°C), turn on A/C (if on same fan circuit) to test fan. Check fan relay, fuse, temp switch.  | Repair fan circuit; reset after cool. |
| **water_pump_degradation** | RPM 3800, Load ~75%, Coolant 102°C (temp rises under load) | Worn impeller or pump failure             | Pressure test cooling system for leaks. Run engine at high RPM and watch ECT; if rises quickly under load, pump issue.  | Replace water pump; refill coolant.   |
| **low_coolant**           | Coolant 77–110°C fluctuating wildly (high SD)              | Air pocket or low coolant level           | Check coolant level; pressure-test for leaks; bleed system. Fluctuating temp often air in housing or failing sensor. | Refill/bleed coolant; replace sensor. |
| **catalyst_degradation**  | O₂ B1S1 & B1S2 both oscillating (random), WR voltage random | Catalytic converter failed (no O₂ buffering) | Measure downstream O₂ vs upstream: if both swing similarly, cat is bad. Perform catalyst efficiency test. | Replace catalytic converter.          |
| **catalyst_restriction**  | Load ~94%, MAF 28 g/s (low), RPM 2800, Speed 40 km/h, Cat Temp ↑ | Clogged/partial cat/exhaust restriction  | Use an exhaust back-pressure gauge. Check turbo wastegate (if turbo). Inspect cat physically. | Repair/replace exhaust/catalyst.      |
| **evap_purge_stuck_open** | Purge 100%, STFT +14%, LTFT +6%, Speed 0 (lean idle)        | Purge solenoid stuck open                 | At idle, disconnect EVAP purge connector: idle should change. With key on, test solenoid coil to chassis (should be open). | Replace purge solenoid.              |
| **o2_sensor_drift**       | LTFT +10%, O₂ B1S2 ~flat (±5 mV around mid)              | Aging O₂ sensor (slow response)           | Wiggle test sensor wiring; check heater circuit. Swap downstream sensor to see if problem follows.  | Replace aging O₂ sensor.             |
| **o2_sensor_failure_low** | O₂ B1S2 stuck at 0 V                                      | O₂ sensor open-circuit or disconnected    | Backprobe sensor: verify wiring and heater. If open, codes P0138/P0139 expected.  | Repair harness or replace sensor.    |
| **o2_sensor_failure_high**| O₂ B1S2 pinned high (0xC8/0.9V)                          | O₂ sensor shorted to voltage             | Similar to above: check wiring; if high, sensor may be shorted power.   | Replace sensor.                      |
| **iat_sensor_failure_cold**| IAT = −40°C (0x00)                                      | IAT sensor open (short to ground)        | Disconnect sensor: reading should go to ambient (~20°C). Short test sensor pins; replace if needed. | Replace IAT sensor.                  |
| **ect_sensor_failure**    | Coolant = −40°C, STFT −10% (rich trim)                    | ECT sensor open (short to ground)        | Same method: unplug ECT, sensor should return ambient. Code P0117. Replace sensor. | Replace ECT sensor.                 |
| **map_sensor_failure**    | RPM 3000, Throttle 44%, Intake Pressure idle-like (e.g. 0x95), MAF 45 g/s | MAP sensor or line failure           | Check MAP with hand-held vacuumsensor; apply vacuum and watch reading. Inspect/replace MAP.  | Replace MAP sensor/hoses.            |
| **tps_failure**          | Throttle stuck ~12%, RPM varies 900–2500 (TPS vs pedal mismatch) | Faulty TPS or throttle body           | Wiggle throttle, check pedal vs TPS voltages (or %). Use scan tool: see if TPS % moves with pedal.  | Replace/calibrate TPS (throttle body). |
| **alternator_failure**   | Control Module Voltage ~12.7 V (running), RPM 1100         | Alternator output weak                  | With A/C on and lights, measure voltage: should be ~14V. Test alternator output current. | Repair/replace alternator.          |
| **voltage_regulator_failure**| Voltage ~15.8 V (running)                              | Overcharging alternator/regulator       | Similar: measure with multimeter. If >14.8V, regulator bad.   | Replace voltage regulator/alternator. |
| **compression_loss**     | RPM 700–1300 unstable, Load ~19%, Throttle ~75%, MAF 22 g/s, STFT +10% | Low compression (worn rings/valves) | Perform relative compression test or use cylinder contribution. Compare to spec.  | Repair: rebuild head or engine.     |
| **head_gasket_leak**     | Coolant 95–115°C erratic, RPM 650–1200 (misfire), STFT +8% | Head gasket blown: coolant in cylinders | Use block tester (combustion gases in coolant); check for white smoke. Cylinder leak-down test.  | Replace head gasket / repair engine. |
| **timing_chain_stretch** | Timing advance low (e.g. 0x18 code), LTFT +7%, Load ~33%, RPM 2400, Speed 55 km/h | Advanced timing off (cam-crank out) | Use scan or cam-crank sync tests. On engines with variable timing, check cam sensor phasing. | Replace chain/tensioner; time engine. |
| **transmission_slip**    | RPM 4200, Speed ~25 km/h, Load ~56%                    | Transmission clutch slip                | Road test in safe area, check gear shifts. Monitor gear ratio PID vs actual RPM. Scan TCM codes. | Repair transmission (clutch, bands). |

### Diagnostic Priority & Next Steps

1. **Scan for Codes:** Many faults set generic DTCs (P0171 lean, P0300 misfire, P0128 thermostat, P0420 cat, P0136 O₂ low, etc.). Use those for clues.  
2. **Live Data Checks:** Verify sensor readings vs reality. E.g. see if TPS moves with pedal, or MAF follows engine load.  
3. **Visual & Mechanical Inspection:** Hoses, wiring, connectors, vacuum leaks, damage. Check fluid levels and quality.  
4. **Sensor/Actuator Tests:** Use multimeter or oscilloscope: check O₂ heater, IAT/ECT resistances, MAP vac-press test.  
5. **Functional Tests:** Swap suspected parts if possible. Use hand-held vacuum on EGR, block EVAP purge, etc.  
6. **Engine Tests:** Compression/leak-down, timing light, fuel pressure gauge, injector balance. 

A simplified **diagnostic flow** for a lean/trim fault might be:

```mermaid
flowchart LR
  A[High Fuel Trim (STFT>10%)] --> B{Is MAF flow low?}
  B -->|Yes| C[Check/Clean MAF sensor]
  B -->|No| D[Suspect vacuum leak]
  D --> E[Smoke-test intake/manifold]
  E --> F{Leak found?}
  F -->|Yes| G[Repair leak]
  F -->|No| H[Check fuel pressure]
  H --> I{Fuel pressure OK?}
  I -->|No| J[Replace pump/filter]
  I -->|Yes| K[Check O₂ sensors for faults]
```

*(This flowchart is a guide: actual diagnosis may involve more steps.)*

## Quick-Test Tips & Safety

- **Fuel Trims:** Take readings at idle and at 2500–3000 rpm. Trims should stabilize near 0%. A *steady* high trim (+15%+) means a real lean condition. 
- **O₂ Sensors:** Use a scope or scan tool to see oscillation. A sluggish post-cat sensor with flat line suggests old converter.  
- **Vacuum Leaks:** Spray carb cleaner (or an unlit propane torch) around intake joints while watching RPM. A leak will cause RPM to rise. Always do this carefully (no open flame!).  
- **Ignition:** Check spark by pulling plug while cranking (ground side of boot). Also compare dwell/pulse width on coil drivers with scan tool if available.  
- **Cooling:** Never remove radiator cap when hot. Use IR thermometer to verify thermostat opening. Ensure coolant level in expansion tank is correct.  
- **Battery/Charging:** Test alternator output at 2000 rpm; verify voltage ~13.8–14.5 V. A battery drain/test isolate for parasitic draw if needed.  
- **Sensor Resistance:** Check IAT/ECT/MAP sensors off-vehicle with multimeter: e.g. at ~20°C, ECT should read ~2.5 kΩ (varies by make), IAT similar. OBD code tables (P0112, etc.) list the expected resistances.  

**Important:** Always ensure the engine is cool and ignition off before touching cooling system parts. When performing drive tests (e.g. transmission), follow safety guidelines (use stands, chocks). For EVAP/EGR tests, release vacuum slowly. Always disconnect battery when servicing electrical components.  

## References

- Official OBD-II PID specifications (SAE J1979)  
- Innova OBD freeze-frame PID definitions (engine sensor behavior and normal ranges)  
- ALLDATA Mass Air Flow Sensor Testing (normal MAF idle values)  
- MOTOR Magazine on Calculated Load (idle load norms)  
- CarParts.com on Catalyst Sensor (catalyst temperature monitoring)  
- Fuel Trim Theory (fuel trim interpretation)  

This sheet prioritizes OEM-standard terms and observations. All diagnostic steps should be confirmed against the specific vehicle’s service manual and in compliance with safety procedures.