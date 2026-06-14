# Chunk preview (220 chunks)

## deep-research-report-diagnostics.md:0

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt defines engine parameters and then applies them to diagnose 31 common faults, includes diagnostic flowcharts, symptom‑to‑cause reasoning, DTC meanings, and step‑by‑step test procedures, which aligns with the fault‑finding focus of the automotive_diagnostics category.

# Automotive Maintenance Basics: PID Definitions and Diagnostics

Modern vehicles use an array of sensors and OBD-II **PIDs** (Parameter IDs) to monitor engine performance. This report defines key engine parameters (STFT/LTFT, MAF, MAP, TPS, O₂ sensors, etc.), their normal ranges and failure modes, and explains how mechanics interpret them. We then apply these concepts to diagnose each of 31 common faults (e.g. vacuum leak, dirty MAF, fuel pump weak, ignition coil failure, thermostat stuck, etc.) using live data and targeted tests. Each fault profile includes an executive summary, a diagnostic flowchart (Mermaid), and practical test tips. Tables compare the faults by affected PIDs, typical DTCs and suggested order of checks. Safety notes and recommended tools (smoke machine, vacuum gauges, fuel pressure tester, etc.) are included where relevant.

## Key Engine Parameters and PIDs

---

## deep-research-report-diagnostics.md:1

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains the operation, voltage characteristics, normal temperature ranges, and baseline behavior of the Engine Coolant Temperature sensor and its PID, which are core fundamentals of automotive sensor operation and OBD-II concepts.

## Key Engine Parameters and PIDs

- **Engine Coolant Temp (ECT)** – A 2-wire **thermistor** immersed in the engine coolant. Resistance *drops* as coolant heats. At ~20°C the ECU sees ~2.0–3.0 V, while at ~90°C it falls to ~0.5–1.0 V. Normal warm temp is ~85–100°C; if ECT stays low (<60°C) the ECU will “think” the engine is cold and enrich fuel (rich trim). A stuck-open thermostat will cause ECT to stay abnormally low (~65°C even when warmed) (diagnose by slow warm-up). If ECT reads an impossible value (e.g. –40°C or constant 5 V), suspect a failed sensor or open circuit. Mechanics often test ECT with an ohmmeter (resistance should match temp) or measure voltage while warming (voltage should drop as coolant heats).

---

## deep-research-report-diagnostics.md:2

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains the basic operation, typical voltage/temperature behavior, and normal ranges of the Intake Air Temperature sensor, which are core concepts of automotive fundamentals rather than fault-finding procedures or broader non‑fundamental topics.

- **Intake Air Temp (IAT)** – A **thermistor** (usually inside the MAF housing or intake) that measures incoming air temperature. Cooler air is denser, so the ECU uses IAT to correct fuel calculation. Typical IAT readings are ambient (~20–25°C = ~3.0 V) at key-on/cold and rise as engine bay heat warms the sensor. A reading stuck near –40°C (0V or 255 code) means an open circuit. Mechanics verify by checking that IAT tracks ambient/engine temperatures or by measuring its resistance vs. temp (NTC sensors have ~2–3 V at 20°C, dropping toward 0.5 V as intake warms).

---

## deep-research-report-diagnostics.md:3

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt explains how to diagnose a faulty MAF sensor, including symptom interpretation (fuel trims >+10%), testing procedures (cleaning, VE test, comparing live readings), and fault signatures, which aligns with diagnostic workflows rather than pure conceptual fundamentals.

- **Mass Air Flow (MAF) Sensor** – Measures the *mass* of intake air (usually in grams/sec). The most common type is a hot-wire sensor placed after the air filter. It outputs a voltage or frequency proportional to airflow. The ECU uses MAF to calculate fuel injection. Typical values depend on engine size and RPM: for example, idle airflow might be a few g/s per liter of displacement, rising to tens of g/s at wide-open throttle. (Technicians often note “engine liters ≈ idle g/s” as a rule of thumb, though it can vary.) A healthy MAF shows fuel trims near 0; if fuel trims exceed ~+10%, suspect misreporting or leaks. Mechanics test it by comparing live MAF readings to known-good specs or performing a volumetric efficiency (VE) test. A common quick check is to clean the MAF with sensor cleaner. Also check for air filter blockage or intake leaks, since any restriction alters MAF output.

---

## deep-research-report-diagnostics.md:4

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains the function, measurement units, typical values, and how the ECU uses MAP sensor data – core concepts of OBD sensor operation, fitting the automotive_fundamentals category.

- **Manifold Absolute Pressure (MAP)** – Measures intake manifold pressure (absolute vacuum) via a diaphragm sensor. The ECU uses MAP (often in kPa or inHg) together with RPM to infer engine load. At idle, MAP ~20–30 inHg (vacuum), rising toward ~29.9 inHg (sea-level) at full throttle. Mechanics verify MAP by checking that it reads near atmospheric (baro) with ignition on, engine off, and drops to ~10–20 inHg at idle. A mismatched MAP (e.g. high vacuum at high RPM) can indicate leaks or sensor fault. The ECU may use MAP for fuel calculation on MAP-based systems.

---

## deep-research-report-diagnostics.md:5

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains what a Calculated Engine Load PID is, how it is defined by SAE, typical percentage ranges, and how it varies with throttle and RPM. This is core knowledge about a PID and its normal behavior, which falls under automotive fundamentals (PIDs, units, healthy baselines, etc.). Although it mentions a diagnostic use case, the primary focus is on describing the PID itself rather than a full fault‑finding workflow.

- **Calculated Engine Load** – A computed PID indicating how “hard” the engine is working (often expressed as a percent of peak load). By SAE definition, it reaches 100% at wide-open throttle regardless of RPM or altitude. On a naturally aspirated engine, idle load might read ~30–50% (in one test ~17% on a VW Passat at 878 RPM). In short, load rises as throttle opens and manifold vacuum falls. Mechanics glance at load vs. RPM: if load stays low despite high throttle, suspect intake/exhaust restriction.

---

## deep-research-report-diagnostics.md:6

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt describes the basic operation, typical voltage ranges, normal baseline values, and failure modes of Throttle Position and Engine RPM sensors, which are core sensor concepts and healthy baseline information rather than step‑by‑step fault diagnosis.

- **Throttle Position (TPS)** – A potentiometer on the throttle plate shaft that outputs a voltage (or %). It indicates throttle opening from closed (~0–10% or ~0.5–1 V) to wide open (usually ~90–100% or ~4.5–5 V). The TPS tells the ECU driver demand. Common failure modes: erratic readings, jumpiness, or “stuck” values. Mechanics test it by comparing voltage or % to throttle angle: idle should be steady near 5–12% (depending on calibration), full throttle ~90%. Codes P0122–P0124 are triggered by TPS anomalies.  

- **Engine RPM (Eng RPM)** – Revolutions per minute of the crankshaft. Measured by crank or camshaft position sensors, this is used by the ECU for timing, fueling and diagnostics. It should rise smoothly with throttle; random fluctuations/misfires will show as rapid RPM swings (especially at idle).

---

## deep-research-report-diagnostics.md:7

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt describes a sensor output (Vehicle Speed), its units, how it influences vehicle behavior, and its role as a scan‑tool parameter—core concepts of sensor operation, units, and baseline behavior rather than fault‑finding or diagnostic procedures.

- **Vehicle Speed (Veh Speed)** – Output from a transmission or wheel speed sensor. Displayed in km/h or mph. It mainly affects shift points and some idle control; not always critical in diagnosis of engine drivability but is a useful scan tool parameter.

---

## deep-research-report-diagnostics.md:8

**Category:** `automotive_diagnostics`  
**Reason:** The passage explains how to interpret O₂ sensor voltages, closed‑loop behavior, and what patterns indicate faults (e.g., failed catalytic converter), which is diagnostic reasoning rather than pure fundamentals or unrelated automotive info.

- **Oxygen Sensors (O₂)** – Zirconia “narrowband” or wideband O₂ sensors sense oxygen in exhaust, generating a voltage (narrowband: 0–1 V) or a ratio/λ signal (wideband). *Bank1 Sensor1 (B1S1)* is the upstream sensor (pre-catalyst) for bank 1 cylinders; *Bank1 Sensor2 (B1S2)* is downstream (post-cat). In closed-loop, a healthy upstream O₂ should swing rapidly between ~0.1 V (lean) and ~0.9 V (rich) around 0.45 V. A smooth oscillation indicates active fuel correction. Downstream O₂ (post-cat) should be much steadier around ~0.4–0.6 V if the cat is good. If *both* sensors oscillate, it suggests a failed catalytic converter. A stuck or erratic O₂ (flat at 0 V or pegged high) indicates a bad sensor. Mechanics use O₂ readings to gauge air-fuel and cat health: rapid swings (B1S1) mean closed-loop is active; a downstream voltage that never changes (or follows the upstream) indicates conversion failure.

---

## deep-research-report-diagnostics.md:9

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt explains how to interpret fuel trim values (STFT/LTFT) to diagnose engine conditions, linking trim percentages to potential faults and describing diagnostic reasoning.

- **Fuel Trims (STFT & LTFT)** – These PIDs show how the ECU is adjusting fuel to maintain stoichiometry. **STFT (Short-Term Fuel Trim)** is the instantaneous correction, **LTFT (Long-Term Fuel Trim)** is the learned adjustment over time. Both are shown as percent. Positive means adding fuel (lean condition), negative means reducing fuel (rich condition). Normally they stay within about ±5%. Values beyond ±10% flag trouble. For example, STFT ~+15–20% means the ECU is adding fuel to compensate for a lean mixture. Mechanics always check trims in multiple conditions: if fuel trims are high only at idle, suspect a vacuum leak; if high at all loads, suspect fuel delivery issues.

---

## deep-research-report-diagnostics.md:10

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt explains how specific OBD-II PIDs (EGR Commanded and EVAP Purge Command) indicate commanded valve positions, interprets abnormal values (e.g., stuck‑open at idle), and links those readings to fault symptoms and diagnostic reasoning.

- **Exhaust Gas Recirculation (EGR) Commanded** – Percent that the ECU is commanding the EGR valve to open (0% = closed, 100% = fully open). A stuck-open EGR (command 100% at idle) will cause rough idle and lean trim. The “Command EGR” PID does not measure flow—only what the computer is telling the valve. When parked, Command EGR should read 0% for a healthy system.  

- **Evaporative Purge (EVAP Purge) Command** – Similar to EGR, this PID shows the duty (0–100%) of the purge solenoid that vents fuel vapors into the intake. 0% = OFF (closed), 100% = ON (open). At idle, purge should normally be off (0%); an EVAP purge stuck on will dump extra fuel vapor, causing rich or lean idle conditions.

---

## deep-research-report-diagnostics.md:11

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt discusses how to interpret catalyst temperature and control module voltage to identify faults (e.g., plugged catalytic converter, alternator/battery issues) and relates these measurements to diagnostic trouble codes, which aligns with fault-finding and diagnostic reasoning rather than core concepts or generic automotive info.

- **Catalyst Temperature** – Many modern systems (especially diesels or high-end cars) have exhaust gas temperature (EGT) sensors before/after the catalytic converter. High catalyst temperature can indicate heavy load or cat restriction. (For example, measuring inlet vs. outlet temp can diagnose a plugged converter.) Typical safe exhaust temps are a few hundred °C; glowing red-black exhaust parts (>750°C) signal problems.  

- **Control Module Voltage** – The system voltage (battery/alternator). Normal running voltage is typically ~13.5–14.5 V. A reading ~12.5 V or lower running indicates a weak alternator/battery; >15 V indicates overcharging. Voltage under ~11 V or above ~16 V can throw codes (P0562 low, P0563 high). Mechanics always check voltage early, since low voltage can cause spurious sensor readings.

---

## deep-research-report-diagnostics.md:12

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains basic concepts such as ignition timing and engine compression, describing how they are measured and what they indicate, which are core automotive fundamentals rather than diagnostic procedures or other automotive information.

- **Ignition Timing (Spark Advance)** – The crankshaft degrees at which spark fires before top dead center (TDC). Reported in degrees (e.g. 10° BTDC). Timing is advanced for load/speed demands and retarded when needed. (In scan data this may appear as “Spark Adv” or timing advance.) Very low advance under light load or erratic values can indicate timing chain/belt issues or sensor faults.  

- **Engine Compression** – Not a PID but a measure of mechanical health. Low compression in one cylinder (due to leaks, worn rings, valve issues) causes misfires and lean trim on that cylinder’s bank. Mechanics verify by compression or leak-down tests.

---

## deep-research-report-diagnostics.md:13

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt discusses using live PIDs and fuel trim data to diagnose specific faults, linking symptom patterns (e.g., high STFT/LTFT with low MAF) to underlying causes, which is characteristic of diagnostic reasoning rather than core concepts or generic automotive info.

In summary, these PIDs form the “alphabet” of the OBD data stream. A mechanic uses live PIDs (via scan tool) plus physical tests to pinpoint issues. For instance, simultaneous high positive STFT/LTFT and low MAF often mean unmetered air (vacuum leak), whereas high fuel trims at all loads suggest fuel delivery problems. Below we apply these principles to diagnose specific faults.

## Fault Comparison Tables

---

## deep-research-report-diagnostics.md:14

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault diagnosis, associated PIDs, DTCs, and a step‑by‑step quick‑check priority for troubleshooting a vacuum leak and dirty MAF sensor, which is classic automotive diagnostic content.

| Fault                       | Primary PIDs Affected                     | Typical DTCs          | Quick Check Priority (fastest to rule out) |
|-----------------------------|-------------------------------------------|-----------------------|-------------------------------------------|
| **Air System:**             |                                           |                       |                                           |
| vacuum_leak                 | STFT↑, LTFT↑, MAF↓, Intake Pressure low, RPM↑ | P0171 (lean B1)       | 1) Visual leaks (hoses, PCV)  2) Smoke test or soapy water  3) Check MAF, IAC<br>4) Fuel trims at idle vs wot |
| dirty_maf                   | MAF↓ (for load), STFT↑, LTFT↑             | P0171 (lean)          | 1) Inspect/clean MAF  2) Check air filter  3) Compare MAF g/s vs RPM (see spec)  4) Fuel trims under load |

---

## deep-research-report-diagnostics.md:15

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures, symptom-to-cause reasoning, DTC codes, and step-by-step diagnostic procedures for specific vehicle issues, which aligns with the 'automotive_diagnostics' category.

| air_filter_restriction      | Throttle↑, MAF↓ (for given RPM), Engine Load↓ | — (lean clues)      | 1) Inspect/replace air filter  2) Smoke test upstream intake  3) Road test trims/wot  4) Fuel trims vs throttle |
| egr_stuck_open              | RPM fluctuating at idle, Commanded EGR 100% | P0400-P0405 (EGR codes) | 1) Scan: Commanded EGR at idle  2) Inspect EGR valve mechanically (stuck open)  3) Bypass or vacuum test EGR  4) Check idle quality |
| **Fuel System:**            |                                           |                       |                                           |
| fuel_pump_weak_load         | STFT↑, LTFT↑ (only under load)             | P0171, P0174 (lean)   | 1) Fuel pressure gauge at idle vs WOT (should hold spec ~40–60 psi)  2) Check fuel pump current draw  3) Inspect fuel filter  4) Observe fuel trims under heavy load |

---

## deep-research-report-diagnostics.md:16

**Category:** `automotive_diagnostics`  
**Reason:** The source file contains diagnostic procedures, symptom-to-cause mappings, DTC interpretations, and step‑by‑step fault‑finding workflows for injector‑related issues, which aligns with the automotive_diagnostics category.

| dirty_injectors             | STFT↑, LTFT↑, possible slight RPM drop     | P0171 (lean)         | 1) Fuel injector balance test or cleaning  2) Fuel pressure (should hold pressure without drop)  3) Injector spray pattern  4) Check ignition coils (to isolate lean spark vs fuel issues) |
| injector_leak              | STFT↓, LTFT↓ (rich trim), rough idle        | P0172 (rich)         | 1) Check fuel rail pressure decay (should not continue rising)  2) Smell for fuel, check spark plug fouling  3) Cylinder drop-out test (remove injector connector)  4) Backpressure on intake with throttle closed |
| injector_stuck_closed      | STFT↑, LTFT↑, RPM ripple at idle          | P0171, P030X (misfire) | 1) Observe misfire on specific cylinder  2) Swap injector with another bank to see if misfire moves  3) Compression test (to rule out mech)  4) Inspect injector resistance/operation |

---

## deep-research-report-diagnostics.md:17

**Category:** `automotive_diagnostics`  
**Reason:** The file contains detailed diagnostic procedures, fault signatures, DTC meanings, symptom-to-cause reasoning, and step‑by‑step troubleshooting workflows for automotive systems, which aligns with the automotive_diagnostics category.

| **Ignition:**               |                                           |                       |                                           |
| ignition_coil_failure      | RPM random (idle), O₂ oscillating, STFT↑   | P030X (misfire)      | 1) Swap coil with another cylinder to see if misfire moves  2) Check coil primary/secondary with multimeter or scope  3) Inspect coil boots/plugs  4) Observe scan data: O₂ sensor swings from misfires |
| spark_plug_wear           | Gradual rise in LTFT (lean), MPG drop      | P030X (misfire)      | 1) Inspect plugs (gap, electrodes)  2) Replace plugs if high mileage (>80k)  3) Check fuel trims after plug change  4) Check ignition timing and coil operation |
| **Cooling:**                |                                           |                       |                                           |

---

## deep-research-report-diagnostics.md:18

**Category:** `automotive_diagnostics`  
**Reason:** The source file contains detailed diagnostic procedures, fault signatures, DTC meanings, and symptom-to-cause reasoning for thermostat and cooling fan issues, which aligns with the automotive_diagnostics category.

| thermostat_stuck_open     | Coolant ~60–70°C even long-run (low ECT)   | P0128 (cold)         | 1) Check coolant temperature vs ambient (should reach ~85–100°C)  2) Test thermostat in pot of water or replace to verify  3) Bypass thermostat to confirm temp rise  4) Fuel trim/rich strategies (cold even when engine has run) |
| thermostat_stuck_closed   | Coolant 105–112°C (high even at idle)      | P0128 (overheat), P0217 | 1) Observe ECT high, fan on constant or won’t engage  2) Check thermostat operation (remove or test)  3) Check radiator flow (overheat at idle, normal at speed)  4) Inspect for head gasket (if random temp swings) |
| cooling_fan_failure_idle  | Coolant ~108°C at idle, drops when moving  | P0128 (overheat idle) | 1) Run engine to temp and see if fan kicks on at high temp (using scan or gauge)  2) If fan fails, test fan motor and relay  3) Verify fan control temp sensor  4) Radiator drain (if hot coolant) safely |

---

## deep-research-report-diagnostics.md:19

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic procedures for specific vehicle symptoms (coolant temperature anomalies, water pump degradation) and includes step‑by‑step fault‑finding guidance, which aligns with the automotive_diagnostics category.

| water_pump_degradation    | Coolant rising under heavy load (e.g. 102°C at high RPM) | —           | 1) Pressure test cooling system (no external leaks)  2) Observe coolant temp vs rpm (should not rise at idle)  3) Check for bearing play, shaft wobble  4) Consider pump replacement if corrosion or impeller worn |
| low_coolant               | Coolant temp erratic (77–110°C), poor heat  | —                   | 1) Check coolant level in reservoir  2) Pressure-test cooling system for leaks  3) Fill and burp system, retest  4) Watch for mix of hot/cold fuel trims (e.g. overrich when perceived cold) |
| **Emissions:**              |                                           |                       |                                           |

---

## deep-research-report-diagnostics.md:20

**Category:** `automotive_diagnostics`  
**Reason:** The source file provides detailed diagnostic procedures for specific fault codes and symptoms, focusing on fault-finding steps, symptom-to-cause reasoning, and diagnostic testing methods. This aligns with the 'automotive_diagnostics' category, which covers fault signatures, DTC meanings, symptom-to-cause reasoning, diagnostic steps, and related workflows. It does not focus on core concepts (automotive_fundamentals) nor general automotive information unrelated to diagnostics (other_automotive_information).

| catalyst_degradation      | O₂ B1S2 swings random, O₂ B1S1 wide (WR)   | P0420 (cat eff.)     | 1) Use scan: if downstream O₂ rapidly swings like upstream, cat is bad  2) Measure backpressure or exhaust vacuum test  3) IR thermometer: inlet vs outlet ~100°F difference expected  4) Inspect/dismantle cat for blockage or meltdown |
| catalyst_restriction      | High engine load, low MAF (like choking), Cat temp ↑ | P0420, P0421    | 1) Vacuum gauge test: vacuum drops continuously under rev  2) Check exhaust backpressure at manifold  3) Temperature test: outlet much hotter than inlet  4) If clogged, usually replace catalytic converter |
| evap_purge_stuck          | Purge=100%, idle trims lean (STFT+14%)     | P0446 (EVAP purge valve) | 1) Scan: EVAP purge commanded on at idle (should be 0%)  2) Visually inspect purge solenoid and hoses (replace if stuck open)  3) Smoke-test EVAP line (leaks also trigger P045X)  4) Disconnect canister purge solenoid to see if idle stabilizes |

---

## deep-research-report-diagnostics.md:21

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic procedures for O₂ sensor failures, linking symptoms to DTCs, and provides step‑by‑step fault‑finding workflows, which fits the automotive_diagnostics category.

| **Sensors:**                |                                           |                       |                                           |
| o2_sensor_drift          | LTFT gradually rises, O₂ B1S2 flat near mid | P0136/P0137 (slow response) | 1) Swap O₂ sensors (upstream/downstream) to isolate failing sensor  2) Check heater circuit (for wideband types)  3) Test with propane enrichment: sensor should go rich quickly  4) Monitor response time on scope |
| o2_sensor_failure_low    | O₂ B1S2 stuck ~0 V (lean)                 | P0136 (low voltage)  | 1) Measure the sensor voltage: if ~0 V regardless of condition, likely open-circuited  2) Check heater fuse (for heated O₂)  3) Replace sensor, confirm downstream.  4) Verify upstream O₂ still oscillates normally |

---

## deep-research-report-diagnostics.md:22

**Category:** `automotive_diagnostics`  
**Reason:** The file contains detailed fault-finding procedures, DTC meanings, symptom-to-cause analysis, and step‑by‑step diagnostic actions for O₂ and IAT sensor failures, which fits the automotive_diagnostics category.

| o2_sensor_failure_high   | O₂ B1S2 stuck ~0.9 V (rich)               | P0137 (high voltage) | 1) Same as above: stuck high indicates short to heater or stuck rich sensor  2) Confirm with meter, replace sensor if needed  3) Check for exhaust leaks downstream (rare cause)  4) Monitor fuel trims (should go lean if sensor removed) |
| iat_sensor_failure_cold  | Intake Temp = –40°C (0x00)               | P0113 (high input)    | 1) Key On: IAT should read ambient. If it reads –40°C, likely open circuit (bad sensor or wiring)  2) Unplug IAT, measure resistance at room temp (typically ~2–3kΩ)  3) Replace sensor or repair wiring, clear code  4) Confirm IAT rises with warm air |

---

## deep-research-report-diagnostics.md:23

**Category:** `automotive_diagnostics`  
**Reason:** The text provides step‑by‑step diagnostic procedures for sensor failures, explains how to interpret DTCs, and uses symptom‑to‑cause reasoning to isolate faults.

| ect_sensor_failure       | Coolant Temp = –40°C, STFT rich (–10%)    | P0117 (low input)     | 1) Similar to IAT: if ECT reads –40°C, suspect open  2) Measure ECT resistance at known temps or test in ice water (should be high resistance ~5–6kΩ at 0°C, decreasing to ~270Ω at 90°C)  3) If open or out-of-spec, replace sensor  4) Verify ECT then follows normal warm-up |
| map_sensor_failure       | RPM ~3000, Throttle ~44%, Intake Pressure idle-like | P0106 (MAP implausible) | 1) Unplug MAP: engine should run extremely poorly; if it still idles fine, suspect stuck MAP  2) Compare MAP vs baro: at key-on, engine-off, they should nearly match  3) Use hand pump: apply vacuum and see if MAP voltage changes smoothly  4) Replace sensor if stuck at one value |

---

## deep-research-report-diagnostics.md:24

**Category:** `automotive_diagnostics`  
**Reason:** The source file provides step‑by‑step diagnostic procedures, fault code interpretation, symptom‑to‑cause reasoning, and troubleshooting workflows for TPS and alternator issues, which aligns with the automotive_diagnostics category.

| tps_failure             | TPS ~fixed (~12%), RPM varies 900–2500    | P0122/P0123 (TPS low/high) | 1) Observe TPS PID: if it never moves, throttle sensor is dead.  2) Check throttle plate: does engine rev without TPS change? (as in fault)  3) Backprobe TPS connector: should see ~0.5 V at closed throttle, rising to ~4.5 V at WOT  4) Replace TPS or throttle body if needed |
| **Electrical:**             |                                           |                       |                                           |
| alternator_failure       | Module Voltage ~12.7 V at idle           | P0562 (voltage low)   | 1) Measure battery voltage at idle: <13 V indicates bad charging  2) Rev engine: voltage should rise above 13.8 V.  3) Check alternator drive belt, connections  4) Test alternator output current or bench-test alternator |

---

## deep-research-report-diagnostics.md:25

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt provides detailed diagnostic procedures, fault signatures, DTC meanings, and symptom-to-cause reasoning for both voltage regulator failure and compression loss, which aligns with the automotive_diagnostics category.

| voltage_regulator_failure | Module Voltage ~15.8 V at idle         | P0563 (voltage high)  | 1) Same as above: >15.0 V indicates overcharging  2) Confirm with load test (lights on)  3) Inspect ground wires/regulator  4) Replace alternator/regulator if overvoltage persists |
| **Mechanical:**             |                                           |                       |                                           |
| compression_loss         | RPM random 700–1300, Throttle ~75%, MAF 22 g/s | P0171 (lean), P030X  | 1) Perform compression test on all cylinders (low compression on affected cylinders indicates leak).  2) Use cylinder balance: disable injectors one by one to find weak one  3) Inspect for vac leaks (head gasket, intake gasket)  4) If mechanical, likely repair by engine rebuild or gasket replacement |

---

## deep-research-report-diagnostics.md:26

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic procedures, fault codes, symptom-to-cause analysis, and repair steps for engine issues, which falls under automotive diagnostics.

| head_gasket_leak         | Coolant random 95–115°C, RPM random 650–1200, STFT+8% | P030X (misfire), P0128 (overheat) | 1) Pressure-test cooling system (see if combustion gases enter coolant)  2) Check oil/fuel for coolant contamination (milky oil)  3) Perform compression test (look for one cylinder low or block balance short-out)  4) Verify with block tester (CO₂ in rad) or inspect for white smoke |
| timing_chain_stretch     | Timing advance low, LTFT+7%, RPM 2400, speed ~55km/h | P0016 (cam/crank corr) | 1) Scope crank and cam signals: confirm cam arrives later than expected (lost tooth/chain stretch).  2) Many cars store P0016–P0018 codes.  3) If PCM-controlled VVT, lock timing (as test) and see if behavior normalizes.  4) Likely repair is chain replacement/timing adjustment |
| **Drivetrain:**             |                                           |                       |                                           |

---

## deep-research-report-diagnostics.md:27

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnosing transmission slip with specific fault-finding steps, symptom-to-cause reasoning, and diagnostic procedures, which aligns with the automotive_diagnostics category.

| transmission_slip        | RPM ~4200, Speed ~25km/h, Engine Load ~56%  | —                     | 1) Check transmission fluid level/condition  2) Perform stall test (watch RPM at stall vs spec)  3) Road test: does dropping to lower gear eliminate slip?  4) Check for tranny codes or pressure loss; may require rebuild or solenoid repair |

---

## deep-research-report-diagnostics.md:28

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic flowcharts and the diagnostic approach for faults, which aligns with fault finding and diagnostic steps, i.e., automotive diagnostics.

*(DTC: Diagnostic Trouble Code. “Priority” lists the logical order of tests – e.g. quick visual/scan checks first, then deeper tests.)*

## Diagnostic Flowcharts

Below are mermaid flowcharts for each fault, illustrating the diagnostic approach from symptoms to fix. (Symbols: `[A]` = data/symptom, `{B}` = decision, `-->` = step).

### Air System Faults

---

## deep-research-report-diagnostics.md:29

**Category:** `automotive_diagnostics`  
**Reason:** The text provides a detailed diagnostic flowchart for air system faults, covering symptom identification, step‑by‑step troubleshooting, and fault isolation, which aligns with the 'automotive_diagnostics' category.

### Air System Faults

```mermaid
flowchart LR
  AL1[Symptom: High idle RPM, STFT/LTFT +15–20% (lean)] --> A1{Inspect intake/PCV hoses}
  A1 -->|Visible leak| A2[Fix/replace leaks (hoses, gaskets)]
  A1 -->|No obvious leaks| A3[Use smoke machine or spray soapy water]
  A3 -->|Leak found| A2
  A3 -->|No leak detected| A4[Check MAF Sensor output (g/s vs spec)]
  A4 -->|MAF reading low| A5[Clean/replace MAF; check air filter]
  A4 -->|MAF normal| A6[Check idle control (IAC) valve or throttle body]
  A6 -->|IAC stuck| A7[Service/replace idle valve]
  A6 -->|IAC OK| A8[Vacuum gauge on intake manifold]
  A8 -->|Low vacuum| A9[Inspect intake manifold gasket/throttle shaft]
  A8 -->|Normal vacuum| A10[Fuel trim stable at higher RPM?]
  A10 -->|No (still lean)| A11[Fuel delivery test (fuel pump, injectors)]
  A10 -->|Yes (only at idle)| A12[Likely vacuum leak persists]

---

## deep-research-report-diagnostics.md:30

**Category:** `automotive_diagnostics`  
**Reason:** The text describes symptoms, diagnostic steps, tools, and repair procedures for a vacuum leak, which falls under fault-finding and diagnostic workflows.

```

**vacuum_leak** (engine vacuum leak): *Summary*: A vacuum leak introduces unmetered air, causing a classic lean condition (STFT/LTFT strongly positive) and often a high or rough idle. Idle RPM may rise (ECU opens throttle for RPM control), then stumble or stall. Diagnosis starts with a visual check of all intake/PCV hoses and gaskets. A smoke test or soapy-water spray on the intake should quickly reveal leaks (the idle will smooth out when the leak is blocked). If leaks are found, replace the bad hose/gasket. If none are obvious, compare MAF output vs engine load; a normal MAF with lean trims still suggests leakage after the MAF. Mechanics then use a vacuum gauge or smoke machine through the throttle body to pinpoint internal leaks (gasket, throttle shaft). Once isolated, repair (e.g. intake manifold gasket). *Tools*: Smoke machine (preferred), vacuum gauge, spray bottle with soapy water. *Safety*: Relieve any residual fuel pressure if spraying intake during warm engine.

---

## deep-research-report-diagnostics.md:31

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt details a step‑by‑step diagnostic flowchart for a lean‑trim condition, including symptom analysis, inspection of the MAF sensor, measurements, leak testing, and further system checks. This is clearly focused on fault finding and diagnostic reasoning rather than general concepts or unrelated automotive information.

```mermaid
flowchart LR
  AL2[Symptom: Lean trims under load; MAF g/s lower than expected for RPM] --> B1{Inspect MAF/filter}
  B1 -->|Dirty/Misaligned| B2[Clean sensor, check air filter, secure boots]
  B1 -->|Looks OK| B3[Measure MAF at various RPM vs spec (scan tool)]
  B3 -->|MAF still low| B2
  B3 -->|MAF normal| B4[Check for intake restrictions or leaks]
  B4 -->|Restrictive air filter| B2
  B4 -->|Leaks downstream| B5[Smoke test after MAF]
  B5 -->|Leak| B6[Repair leak]
  B5 -->|No leak| B7[Engine tuning: check fuel system]

---

## deep-research-report-diagnostics.md:32

**Category:** `automotive_diagnostics`  
**Reason:** The text explains how to diagnose a faulty MAF sensor, including symptom interpretation, testing procedures, and tool usage, which fits the diagnostic category.

```

**dirty_maf** (dirty or faulty MAF sensor): *Summary*: A fouled MAF underreads airflow, making the ECU inject too little fuel (result: positive trims, lean running). Common sign: fuel trims spike under load (while idle may seem okay) and poor power. First inspect/clean the MAF element (hot-wire) with specialized cleaner. Also replace/inspect air filter. If cleaning doesn’t fix it, test MAF voltage/frequency output with a scan tool. Compare the MAF reading (in g/s) to what the engine should see at given RPM/load (many scanners have spec modes). A misreporting MAF often triggers lean P-codes (P0171). If MAF is good but trims still lean, check for vacuum leaks or fuel issues. *Tools*: MAF cleaner spray, multimeter or lab scope on MAF, scan tool recording.

---

## deep-research-report-diagnostics.md:33

**Category:** `automotive_diagnostics`  
**Reason:** The text presents a step‑by‑step diagnostic flowchart for troubleshooting a specific symptom (low MAF reading with high throttle), describing fault‑finding logic, symptom‑to‑cause reasoning, and diagnostic actions. This fits the definition of automotive_diagnostics.

```mermaid
flowchart LR
  AL3[Symptom: ↑Throttle %. MAF ↓ for given RPM (e.g. throttle 63%, MAF 35g/s), low load] --> C1{Inspect air filter & throttle body}
  C1 -->|Blocked air filter| C2[Replace air filter]
  C1 -->|Throttle dirty| C3[Clean throttle body]
  C3 --> C2
  C1 -->|OK| C4[Check MAF voltage/output]
  C4 -->|MAF output low| C5[Clean/replace MAF]
  C4 -->|MAF output normal| C6[Check for intake air restriction (e.g. collapsed hose)]
  C6 -->|Restriction found| C2
  C6 -->|Clear| C7[Perform power/acceleration test]
  C7 -->|Power OK| C8[No fault (normal performance loss)]
  C7 -->|Sluggish| C9[Check for vacuum leak (see vacuum_leak)]

---

## deep-research-report-diagnostics.md:34

**Category:** `automotive_diagnostics`  
**Reason:** The chunk describes diagnosing a clogged air filter causing engine lugging, linking symptoms (high throttle, low MAF, low load) to cause, and provides step‑by‑step diagnostic actions (visual inspection, filter replacement, checking intake tubes, wastegates, MAF vs throttle comparison). This fits the diagnostic workflow rather than core concepts or generic automotive info.

```

**air_filter_restriction** (intake filter clogged or duct restricted): *Summary*: A clogged air filter or intake yields high throttle angle but low MAF and engine load, causing lugging. The engine struggles even with throttle up. First, visually inspect and replace a dirty air filter. Next, remove the filter and check if performance normalizes. Also, check for collapsed intake tubes or stuck wastegates (turbo cars). Because high throttle but low load mimics engine struggling, mechanics confirm by checking MAF vs throttle. If restriction is cleared and performance returns, problem solved. If not, proceed as in other MAF tests. *Safety*: Ensure engine is off and air box snap-locks are secure after servicing.

---

## deep-research-report-diagnostics.md:35

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt presents a step‑by‑step diagnostic flowchart for a rough‑idle symptom, including symptom description, scan‑tool command verification, inspection of EGR components, vacuum leak testing, and decision logic for fault isolation. This is classic fault‑finding / diagnostic reasoning rather than a core concept explanation or generic automotive reference, so it belongs to the automotive_diagnostics category.

```mermaid
flowchart LR
  AL4[Symptom: Rough idle, random RPM 600–1200, EGR Cmd=100%, mild lean trim] --> D1{Scan Tool: Commanded EGR=100% at idle?}
  D1 -->|Yes| D2[Inspect EGR valve (vacuum or plate)]
  D2 -->|Stuck open| D3[Clean or replace EGR valve]
  D2 -->|OK free-moving| D4[Check EGR solenoid/vacuum line]
  D4 -->|Faulty solenoid/line| D3
  D4 -->|Functioning| D5[Perform intake vacuum leak test (hold valve closed)]
  D5 -->|Idle smooths| D6[Likely vacuum/electrical fault to EGR]
  D5 -->|Still rough| D7[Engine control: check EGR-related codes or replace valve]

---

## deep-research-report-diagnostics.md:36

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a specific fault (EGR valve stuck open), its symptoms, diagnostic steps, and tools to verify and fix it, which falls under fault-finding and diagnostic reasoning.

```

**egr_stuck_open** (EGR valve stuck open): *Summary*: If the EGR valve is stuck fully open, too much exhaust gas enters at idle, causing unstable idle (fluctuating 600–1200 RPM) and a mild lean condition. The scan tool will show *Commanded EGR* at 100%. Quick check: with engine idling, manually close EGR (if vacuum-operated) and see if idle stabilizes. If so, replace/clean the valve or solenoid. Also inspect the vacuum line/control circuit. Confirm with a stethoscope on the EGR cooler (if applicable) or by unplugging EGR (engine should improve if it was the problem). No EGR DTC may be present. *Tools*: Scan tool to read EGR command, vacuum pump or meter, replacement EGR valve or gasket.  

### Fuel System Faults

---

## deep-research-report-diagnostics.md:37

**Category:** `automotive_diagnostics`  
**Reason:** The text presents a diagnostic flowchart for fuel system faults, describing symptom interpretation, testing steps, and fault isolation, which aligns with fault-finding and diagnostic reasoning rather than core concepts or generic automotive info.

### Fuel System Faults

```mermaid
flowchart LR
  F1[Symptom: Lean trims NORMAL at idle; under heavy load LTFT+15%, STFT+20%] --> G1{Fuel pressure test}
  G1 -->|Pressure falls under load| G2[Suspect weak fuel pump or filter]
  G1 -->|Pressure OK| G3[Inspect injectors (flow test)]
  G2 --> G4[Replace fuel pump/filter]
  G3 -->|Injector flow low| G5[Clean/replace injectors]
  G3 -->|Injectors OK| G6[Check for intake leaks or ECU issues]

---

## deep-research-report-diagnostics.md:38

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnosing a specific fault (weak fuel pump causing lean trims under load), includes symptom-to-cause reasoning, measurement steps, and tool usage, which fits the diagnostics category.

```

**fuel_pump_weak_load**: *Summary*: A weak fuel pump or clogged filter may maintain idle but starve fuel under load, causing lean trims only when accelerating. First measure fuel rail pressure at idle and during full throttle: it should stay at manufacturer spec (often ~40–60 psi). A significant drop under load implicates the pump or filter. Inspect/replace fuel filter (cheap first) and measure current draw on pump. If pump voltage is good but pressure low, replace pump. Also check for kinks in fuel line. *Tools*: Fuel pressure gauge, current clamp or multimeter, fuel filter spanner. *Safety*: Relieve fuel pressure before disconnecting lines.

---

## deep-research-report-diagnostics.md:39

**Category:** `automotive_diagnostics`  
**Reason:** The snippet presents a step‑by‑step diagnostic flowchart for troubleshooting a specific engine symptom (high idle instability with positive fuel trims), covering fault signatures, symptom‑to‑cause reasoning, and diagnostic decision paths, which aligns with the automotive_diagnostics category.

```mermaid
flowchart LR
  FI1[Symptom: Slight high idle instability, positive fuel trims] --> H1{Fuel injector balance}
  H1 -->|One injector weak| H2[Clean or replace that injector]
  H1 -->|All injectors similar| H3{Spark/injection sync}
  H3 -->|Misfires observed| H4[Swap with coil/plugs test]
  H3 -->|No misfire| H5[Consider vacuum leak or sensor drift]

---

## deep-research-report-diagnostics.md:40

**Category:** `automotive_diagnostics`  
**Reason:** The text describes symptom-to-cause reasoning, diagnostic steps, and interpretation of fuel trim and misfire codes to identify and address injector-related faults, which aligns with the automotive_diagnostics category.

```

**dirty_injectors**: *Summary*: Fuel injectors that are partially clogged or not spraying properly cause a lean mixture (+STFT) and roughness. If trims are moderately positive and there’s mild instability, an injector flow test or cleaning may help. Mechanics can perform an injector balance test or use professional ultrasonic cleaning. Also inspect spark/plugs to rule out ignition problems. If fuel trims are still high after cleaning, and fuel pressure is good, consider injector replacement. No single DTC identifies this; look for lean codes (P0171) and misfire codes (P030x).

```mermaid
flowchart LR
  FI2[Symptom: Rich fuel trims (STFT –18%, LTFT –12%), likely misfire] --> I1{Check injector for leak}
  I1 -->|Fuel dripping when off| I2[Replace leaking injector]
  I1 -->|No leak| I3[Check fuel pressure relief]
  I3 -->|Pressure still on| I2
  I3 -->|Normal] I4{Other causes}
  I4 --> Prexhaust]] Oₓ sensors

---

## deep-research-report-diagnostics.md:41

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnosing a leaking fuel injector, its symptoms, fault codes, and diagnostic steps, which falls under fault-finding and diagnostic reasoning.

```

**injector_leak**: *Summary*: A leaking injector dumps fuel into the intake (or cylinder) even at idle, causing a rich mixture (negative trims) and poor idle. Look for wet spark plugs, fuel smell, or pressure that remains high after shutting off the engine. A simple test is to hold the injector open (with ignition off) and watch for dripping fuel. If confirmed, replace the injector. Also inspect O-rings and fuel rail. This often triggers rich-codes like P0172. *Tools*: Fuel pressure gauge (to see if pressure decays slowly), injector test bench or careful live test with caution (hot engine). *Safety*: Beware of fuel spray; relieve pressure and wear eye protection.

---

## deep-research-report-diagnostics.md:42

**Category:** `automotive_diagnostics`  
**Reason:** The text presents a step‑by‑step diagnostic flowchart for troubleshooting a lean idle/misfire condition, covering symptom analysis, testing procedures, and fault isolation – classic automotive diagnostics.

```mermaid
flowchart LR
  FI3[Symptom: Lean trims, random idle, possible misfire at idle] --> J1{Injector driver test}
  J1 -->|Injector not firing| J2[Check injector wiring/fuse/driver]
  J1 -->|Injector fires| J3[Check fuel flow to injector]
  J3 -->|No fuel flow| J4[Inspect fuel rail, pump]
  J3 -->|Fuel present| J5[Swap injector; if idle smooths, injector bad]
  J5 -->|No change| J6[Inspect vacuum leak at intake]

---

## deep-research-report-diagnostics.md:43

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a specific fault symptom (injector stuck closed) and diagnostic steps to identify and test the injector, which falls under fault finding and diagnostic reasoning.

```

**injector_stuck_closed**: *Summary*: If an injector fails (clogs) closed, its cylinder becomes very lean and misfires at idle, causing high trims on that bank. The symptom is unstable idle and lean codes (P0171) possibly with misfire code. A quick test is to temporarily disable one injector (unplug while running); the missing cylinder should cause a noticeable RPM drop. If unplugging one fixes the imbalance, that injector is suspect. Replacement of the bad injector usually resolves it. 

### Ignition Faults

---

## deep-research-report-diagnostics.md:44

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a diagnostic flowchart for ignition faults, including symptom analysis, code scanning, component testing, and inference steps to isolate causes such as misfire, coil/plug failure, injector issues, and fuel pressure problems. This is clearly focused on fault-finding and diagnostic reasoning rather than core concepts or general automotive information.

### Ignition Faults

```mermaid
flowchart LR
  IG1[Symptom: Idle surge (RPM swings 500–1500), O₂ B1S2 erratic, STFT+6%] --> K1{Scan for misfire codes}
  K1 -->|P030x present| K2[Suspect coil or plug on that cylinder]
  K2 --> L1[Swap coil/plug with another cyl]
  L1 -->|Misfire moves| K3[Replace that coil/plug]
  L1 -->|Stays same| K4[Check injector or compression]
  K1 -->|No codes| K5{Check live O₂ waveforms}
  K5 -->|One cylinder lean spike| K2
  K5 -->|All cylinders erratic| K6[Check fuel pressure, sensor drift]

---

## deep-research-report-diagnostics.md:45

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault-finding procedures for ignition coil failure, including symptom analysis, diagnostic steps, tool usage, and code interpretation, which aligns with automotive diagnostics.

```

**ignition_coil_failure**: *Summary*: A bad ignition coil causes random misfires (especially at idle), which the ECU corrects by opening throttle and adding fuel (thus STFT slightly positive). Live data will show unstable RPM and O₂ sensor oscillations (often the downstream O₂ will swing as if a fresh unburnt charge is entering). Diagnostically, scan tool may show a misfire code (P030x). Swap suspected coil with another cylinder: if misfire moves, replace the coil. Also check spark plug condition and ignition wires. *Tools*: Spark tester, oscilloscope or coil tester, scan tool to identify misfire cylinder.

```mermaid
flowchart LR
  IG2[Symptom: Slowly increasing LTFT (+9%), small STFT (+6%)] --> M1{Inspect spark plugs}
  M1 -->|Electrodes worn| M2[Gap/Replace plugs]
  M1 -->|OK| M3{Check ignition timing}
  M3 -->|Timing retarded| M4[Adjust/repair timing]
  M3 -->|Timing normal| M5[Check for vacuum leak or small fuel issue]

---

## deep-research-report-diagnostics.md:46

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains fundamental concepts such as lean condition, long-term fuel trim, spark plug wear, ECU behavior, and sensor operation, which are core automotive fundamentals rather than diagnostic steps or other peripheral information.

```

**spark_plug_wear**: *Summary*: Worn spark plugs cause a lean but not catastrophic condition: the ECU gradually adds fuel, so LTFT creeps positive. The result is slightly poorer economy and mild roughness. Typically no DTC until misfire gets bad. The first fix is to inspect and replace high-mileage plugs. Check spark advance (a retarded or erratic timing could exacerbate wear effects). After new plugs, trims should return to normal. 

### Cooling System Faults

```mermaid
flowchart LR
  C1[Symptom: Coolant ~65°C after long run, only ∼] --> N1{Check thermostat operation}
  N1 -->|Stuck open| N2[Replace thermostat]
  N1 -->|Thermostat OK| N3[Check coolant level/sensor]
  N3 -->|Low coolant| N4[Top off, pressure test]
  N3 -->|Sensor error| N5[Replace ECT sensor]

---

## deep-research-report-diagnostics.md:47

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a specific fault (thermostat stuck open), symptom analysis, diagnostic steps, flowchart, and troubleshooting workflow, which aligns with automotive diagnostics rather than core fundamentals or generic automotive information.

```

**thermostat_stuck_open**: *Summary*: The engine never reaches normal operating temperature, sticking at ~60–70°C even after long driving. On scan, ECT stays low and fuel trims may be rich (ECU enriches for cold running). P0128 may be thrown. First check coolant level and sensor (a false reading of “cold” can mimic this). If sensor is good, the thermostat is likely failed open. Replace thermostat (engine block temperature should rise to ~85–100°C). *Tools*: Infrared thermometer, scan tool ECT reading, simple cold test of thermostat in water.  

```mermaid
flowchart LR
  C2[Symptom: Coolant ~105–112°C, even at idle] --> O1{Check thermostat}
  O1 -->|Stuck closed| O2[Replace thermostat]
  O1 -->|OK| O3{Check coolant flow}
  O3 -->|No flow| O2
  O3 -->|Flow present| O4{Check radiator fan}
  O4 -->|Fan not running at temp| O5[Repair fan/circuit]
  O4 -->|Fan OK| O6[Check for external blockage or head gasket]

---

## deep-research-report-diagnostics.md:48

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a diagnostic workflow for a symptom (engine overheating) and outlines steps to test and confirm the cause (thermostat stuck, fan issue), which is characteristic of fault-finding and diagnostic reasoning.

```

**thermostat_stuck_closed**: *Summary*: The engine overheats quickly to ~110°C at idle. The scan tool shows ECT pegged high. If the thermostat is stuck shut, coolant can’t circulate into radiator, causing overheat. First confirm thermostat operation (feel upper hose – should stay cold if stat is stuck). Replace thermostat and retest. Also ensure the radiator fan works when hot (some cars trip a DTC if fan doesn’t engage).  

```mermaid
flowchart LR
  C3[Symptom: Coolant ~108°C only at idle (speed=0)] --> P1{Start engine in neutral}
  P1 -->|Temp rises, fan should engage| P2[If fan dead, replace fan or control module]
  P1 -->|Works OK| P3{Test under load}
  P3 -->|Still overheats| P4[Suspect restriction (blocked rad) or airlock]
  P3 -->|OK} P5[Likely fan issue only at idle]

---

## deep-research-report-diagnostics.md:49

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a specific fault (cooling fan failure causing overheating at idle) and provides a step‑by‑step diagnostic flowchart to identify the root cause, which aligns with fault‑finding and diagnostic reasoning rather than core concepts or generic automotive information.

```

**cooling_fan_failure_idle**: *Summary*: The engine only overheats at idle (speed=0) and stays normal when driving. This means the radiator fan is not turning on at low RPM. Check fan operation: jump power to fan or check its relay/fuse. Often the fan must be replaced if seized, or the temperature sensor may be faulty.  

```mermaid
flowchart LR
  C4[Symptom: Temp 102°C at high RPM/load] --> Q1{Pressure test cooling system}
  Q1 -->|Leaks present| Q2[Repair leak]
  Q1 -->|No leaks| Q3{Inspect water pump}
  Q3 -->|Corrosion/cavitation| Q4[Replace water pump]
  Q3 -->|Pump OK| Q5{Check thermostat cycling}
  Q5 -->|Never closes| Q2
  Q5 -->|Closes normally| Q6[Investigate radiator blockage or coolant viscosity]

---

## deep-research-report-diagnostics.md:50

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a specific fault (water pump degradation) and provides a diagnostic workflow, symptom analysis, and step‑by‑step troubleshooting, which fits the diagnostics category rather than fundamentals or other automotive information.

```

**water_pump_degradation**: *Summary*: With sustained high RPM (e.g. highway), coolant climbs near 102°C. Likely the pump’s impeller is slipping (cavitation or worn blades) and can’t circulate fast enough under high flow. First pressure test for leaks. Check the pump for coolant weep or bearing play. If pump blades are corroded or worn, replace pump. Also verify thermostat and radiator.  

```mermaid
flowchart LR
  C5[Symptom: Coolant erratic 77–110°C (high std dev)] --> R1{Check coolant level and sensor}
  R1 -->|Low coolant| R2[Top up and pressure test]
  R1 -->|Sensor issue| R3[Replace ECT sensor]
  R1 -->|Wiring/corrosion| R3
  R1 -->|None of above| R4[Likely head gasket or airlock]

---

## deep-research-report-diagnostics.md:51

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt discusses diagnosing intermittent coolant temperature issues and emissions-related fault codes (e.g., P0420), symptom-to-cause reasoning, and step‑by‑step diagnostic workflows, which aligns with the automotive_diagnostics category.

```

**low_coolant**: *Summary*: Random coolant temps suggest intermittent contact or low coolant. If ECT swings wildly, check coolant level first. A low reservoir can introduce air pockets. Pressurize the system to find leaks. An open ECT wire or intermittent connector can also mimic this (voltage drop). Fix by topping and burping coolant; replace leaking hoses/sensors. If problem persists, consider head gasket (combustion gases pushing coolant sporadically). 

### Emissions Faults

```mermaid
flowchart LR
  EM1[Symptom: O₂ B1S1 and B1S2 both oscillating rapidly] --> S1{Read codes (e.g. P0420)}
  S1 -->|P0420| S2[Inspect/replace catalytic converter]
  S2 --> S3[Check O₂ sensor operation]
  S1 -->|No cat code| S4[Could be high-flow aftermarket cat or sensor issue]
  S4 --> S3
  S3 -->|Sensors OK| S2
  S3 -->|One sensor bad| S5[Replace sensor]

---

## deep-research-report-diagnostics.md:52

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses diagnosing catalyst degradation, interpreting O₂ sensor behavior, P0420 codes, temperature tests, and fault-finding workflows, which falls under fault finding and diagnostic reasoning.

```

**catalyst_degradation**: *Summary*: If the downstream O₂ sensor (post-cat) mimics the upstream (oscillating 0.1–0.9 V), the cat is likely ineffective. The scan tool will often show a P0420 code (“catalyst efficiency below threshold”). Quick tests: with an infrared thermometer, the cat outlet should be significantly hotter (~50–150°F) than the inlet under steady load. A clogged or disintegrating cat fails to burn off unburned gases, so its efficiency drops. The cure is usually catalytic converter replacement.  

```mermaid
flowchart LR
  EM2[Symptom: High load (~94%), MAF low (28g/s), cat temp rises] --> T1{Check vacuum at idle (w/Gauge)}
  T1 -->|Drops then rises then levels| T2[Cat likely OK]
  T1 -->|Continues to drop| T3[Suspect clogged cat]
  T3 --> U1{Perform exhaust temp test}
  U1 -->|Inlet << outlet temp (>100°F diff)| T4[Cat working - check engine (e.g. unburnt fuel)]
  U1 -->|Outlet much hotter| T3
  T4 --> V1[Clogged or damaged cat]

---

## deep-research-report-diagnostics.md:53

**Category:** `automotive_diagnostics`  
**Reason:** The text describes symptom analysis, diagnostic steps, and fault-finding procedures for a catalytic converter restriction and EVAP purge system, which aligns with fault finding and diagnostic reasoning.

```

**catalyst_restriction**: *Summary*: A physically blocked catalytic converter (“cat restriction”) causes high exhaust backpressure. Symptoms: poor acceleration, low MAF flow at high throttle, and exhaust heat build-up (see fault chart). The vacuum gauge test can indicate it: normally vacuum drops when revving then returns; a continued drop suggests a restriction. An IR thermometer will show the catalyst outlet much hotter than normal. The fix is cat replacement.    

```mermaid
flowchart LR
  EM3[Symptom: Purge=100% at idle, STFT +14%, lean idle] --> U2{Check EVAP purge command}
  U2 -->|Stuck ON| U3[Unplug purge solenoid]
  U3 -->|Idle improves| U4[Replace purge valve/solenoid]
  U2 -->|OK (0%)| U5[Look for vacuum leak or fuel trim issue]

---

## deep-research-report-diagnostics.md:54

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt details diagnostic procedures for a stuck‑open EVAP purge valve and a flowchart for troubleshooting O₂ sensor behavior, focusing on fault identification and repair steps rather than core concepts or general automotive info.

```

**evap_purge_stuck**: *Summary*: A stuck-open EVAP purge valve dumps fuel vapor into the intake at idle, causing lean condition (ECU injects more gas to compensate). The scan tool will show *Evap Purge* at 100% command even at idle. To diagnose, confirm command and then disconnect or disable the purge solenoid: if idle normalizes, replace the solenoid. Also pressure-test the EVAP canister lines. Typically no direct DTC (unless char layer fault). *Tools*: Hand vacuum pump on purge valve, scan tool to command off/on, replacement solenoid.

### Sensor Faults

```mermaid
flowchart LR
  SN1[Symptom: LTFT slowly rising, O₂ B1S2 nearly constant] --> V1{O₂ sensor heat-up test}
  V1 -->|Slow to respond| W1[Replace O₂ sensor (Bank 1 Sensor 2)]
  V1 -->|Normal| W2[Check wiring/connectors]

---

## deep-research-report-diagnostics.md:55

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic procedures for O₂ sensor drift and failure, including symptom analysis, fault signatures, step‑by‑step checks, and flowchart‑based troubleshooting, which aligns with the automotive_diagnostics category.

```

**o2_sensor_drift**: *Summary*: A drifting (sluggish) downstream O₂ sensor manifests as slow fuel trim drift (+LTFT) and a relatively flat O₂ output. Check by cycling fuel mixture (propane or throttle blip) and watch the sensor: if it lags, replace it. Bank1S2 failures often only give lean or rich DTC if severe. *Tools*: Propane enrichment or live data logging.  

```mermaid
flowchart LR
  SN2[Symptom: O₂ B1S2 stuck at 0.0V] --> X1{Sensor check}
  X1 -->|Heater fault| X2[Check heater fuse/wiring]
  X1 -->|None| X3[Replace O₂ sensor (B1S2)]
```

**o2_sensor_failure_low**: *Summary*: Downstream O₂ stuck at ~0 V means it’s not registering any oxygen. Check its heater circuit and wiring. If those are fine, replace the sensor. Codes will be P0133 or P0137.  

```mermaid
flowchart LR
  SN3[Symptom: O₂ B1S2 stuck at high (0.9V)] --> Y1{Sensor check}
  Y1 -->|Sensor wiring short| Y2[Repair wiring]
  Y1 -->|No wiring fault| Y3[Replace O₂ sensor (B1S2)]

---

## deep-research-report-diagnostics.md:56

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic procedures, symptom-to-cause analysis, and fault signatures for O₂ and IAT sensor failures, which aligns with automotive diagnostics rather than fundamentals or other automotive information.

```

**o2_sensor_failure_high**: *Summary*: Downstream O₂ stuck at high voltage (~0.9V) typically means it thinks the mixture is always rich. This often indicates a shorted sensor. Code is P0137. Diagnosis is similar to above.  

```mermaid
flowchart LR
  SN4[Symptom: Intake Temp = –40°C (0x00)] --> Z1{Check IAT sensor}
  Z1 -->|Open circuit| Z2[Replace IAT sensor]
  Z1 -->|Short to ground| Z3[Repair wiring]
```

**iat_sensor_failure_cold**: *Summary*: IAT reading –40°C (hex 0x00) means it’s pegged cold (circuit open). Verify by unplugging sensor: if the PID reads fixed extreme, replace the IAT. Before replacing, ensure the sensor (or an internal ECU IAT in the MAF) is not actually in extremely cold air. Code P0113 often appears.  

```mermaid
flowchart LR
  SN5[Symptom: Coolant Temp = –40°C] --> A20{Check ECT sensor and circuit}
  A20 -->|Open circuit detected| A21[Replace ECT sensor]
  A20 -->|Short to ground| A22[Fix wiring]

---

## deep-research-report-diagnostics.md:57

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes fault-finding workflow, symptom-to-cause reasoning, DTC interpretation, and diagnostic steps for sensor failures, which aligns with the diagnostics category.

```

**ect_sensor_failure**: *Summary*: ECT reading –40°C indicates an open or failed coolant temp sensor. Verify by reading resistance or voltage at the sensor vs. expected (see table in [30]). Replace the sensor if open. A P0117 or P0118 code usually logs. 

```mermaid
flowchart LR
  SN6[Symptom: MAP (intake pressure) at idle (~95 kPa) but RPM ~3000 and throttle 44%] --> B20{Compare MAP vs Baro (engine off)}
  B20 -->|Mismatch or fixed high| B21[Suspect MAP sensor]
  B21 -->|MAP unplugged engine dies?| B22[Replace MAP sensor]

---

## deep-research-report-diagnostics.md:58

**Category:** `automotive_diagnostics`  
**Reason:** The snippet describes a specific fault symptom (MAP sensor reading incorrectly), diagnostic steps to verify and replace the sensor, and flowchart of diagnostic reasoning, which aligns with fault-finding and diagnostic workflows.

```

**map_sensor_failure**: *Summary*: If MAP reads “idle” (high vacuum) while engine is revving with the throttle partially open, the MAP is lying. Test by comparing MAP reading to barometric pressure with ignition on, engine off (should match). If MAP is stuck around one value, replace it. On some cars an unplugged MAP will either kill the engine or throw P0106. 

```mermaid
flowchart LR
  SN7[Symptom: TPS ~12% stuck, RPM varies] --> C20{Check throttle actuator}
  C20 -->|Throttle body mechanically fine| C21[TPS sensor out of range]
  C20 -->|Throttle misaligned| C22[Adjust/rebuild throttle]
  C21 --> C23[Replace TPS sensor]

---

## deep-research-report-diagnostics.md:59

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic procedures for throttle position sensor failures and electrical faults, including symptom analysis, fault codes, and step‑by‑step troubleshooting, which aligns with the fault‑finding focus of the automotive_diagnostics category.

```

**tps_failure**: *Summary*: A fixed TPS (e.g. stuck at ~12%) means the ECU sees a constant small throttle even as you press the pedal. Diagnose by manually moving the throttle: the reported TPS should move accordingly (from ~0% up to 100% when fully open). If it doesn’t, replace the TPS or throttle body assembly. Codes P0122/P0123 will flag extreme low/high TPS.  

### Electrical Faults

```mermaid
flowchart LR
  EL1[Symptom: System Voltage ~12.7 V running] --> D20{Check alternator output}
  D20 -->|Low output| D21[Test/replace alternator}

---

## deep-research-report-diagnostics.md:60

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnosing an alternator charging issue, interpreting voltage readings, checking for a P0562 code, and outlining diagnostic steps and possible causes, which fits the diagnostics category.

```

**alternator_failure**: *Summary*: An alternator that only charges to ~12.7 V is weak. Use a multimeter: at idle it should be ~13.5–14.5 V. If it stays near battery rest voltage (~12.6 V) on startup and under load, the alternator is failing. Check belt tension and connections first, then rebuild or replace the alternator. A P0562 code may be logged.  

```mermaid
flowchart LR
  EL2[Symptom: Voltage ~15.8 V] --> E20{Verify with meter under load}
  E20 -->|Still high| E21[Replace voltage regulator/alternator]
  E20 -->|Normalizes| E22[Intermittent regulators or wiring]

---

## deep-research-report-diagnostics.md:61

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnosing a voltage regulator failure and a mechanical fault using symptom analysis, compression testing, and fault isolation, which falls under fault-finding and diagnostic reasoning.

```

**voltage_regulator_failure**: *Summary*: High charging voltage (>15 V) indicates a bad regulator. Confirm with meter on battery: if it persists >15 V at various RPM or loads, the alternator/regulator is bad. Replace alternator (or regulator if serviceable).  

### Mechanical Faults

```mermaid
flowchart LR
  ME1[Symptom: Throttle ~75%, MAF low 22g/s, RPM & idle unstable] --> F20{Compression test}
  F20 -->|Cylinder(s) low| F21[Locate leak-down: likely head gasket or valve]
  F20 -->|Compression normal| F22[Check for intake/exhaust restrictions]

---

## deep-research-report-diagnostics.md:62

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault-finding steps, symptom interpretation, compression testing, leak-down analysis, and diagnostic decision pathways for a specific engine issue.

```

**compression_loss**: *Summary*: This fault profile mimics a cylinder losing compression (or intake). High throttle with low MAF suggests the engine is “choking” (a big air leak or compression loss). Perform a cylinder pressure test: if one cylinder is low, inspect valves or gasket. If all cylinders low by a similar amount, consider intake manifold leak. Fix accordingly (engine rebuild or gasket replacement). Unbalanced cylinders also often cause lean trim on that bank (P0171).  

```mermaid
flowchart LR
  ME2[Symptom: Coolant random 95–115°C + misfire] --> G20{Compression & leak-down}
  G20 -->|Air in coolant test positive| G21[Replace head gasket]
  G20 -->|Compression varying| G21
  G20 -->|Both tests normal| G22[Suspect thermostat/fan or sensor]

---

## deep-research-report-diagnostics.md:63

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a diagnostic process for a head gasket leak, including symptom analysis, specific tests (block leak-down, compression test), and decision-making steps to confirm and fix the issue. This is clearly about fault-finding and diagnostic reasoning rather than core concepts or general automotive information.

```

**head_gasket_leak**: *Summary*: A failing head gasket causes coolant to heat unpredictably and sometimes misfire (coolant burning in cylinder). Diagnosis: perform a block leak-down (combustion leak) test using a chemical CO₂ tester on the radiator. Also compression test (one cylinder may compress into the cooling system). If confirmed, replace the head gasket (or heads).  

```mermaid
flowchart LR
  ME3[Symptom: Timing advance low, LTFT+7%, subtle power loss] --> H20{Check timing belt/chain alignment}
  H20 -->|Skip detected| H21[Replace chain/tensioner]
  H20 -->|Cam/crank out-of-phase| H21
  H20 -->|No obvious skip| H22[Scope cam vs crank (P0016)]
  H22 -->|Mismatch| H21
  H22 -->|Match| H23[Check variable valve timing actuator]

---

## deep-research-report-diagnostics.md:64

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes diagnosing drivetrain slip, checking transmission fluid, scanning for codes, and interpreting fault signatures – classic fault‑finding workflow.

```

**timing_chain_stretch**: *Summary*: A stretched timing chain makes ignition/fuel timing lag (low spark advance) and causes partial misfire. Look for P0016 cam-crank correlation codes. The solution is to replace the chain, guides, and tensioners, and reset cam timing.  

### Drivetrain Faults

```mermaid
flowchart LR
  DR1[Symptom: RPM 4200, Speed ~25 km/h (slip)] --> I20{Transmission fluid level}
  I20 -->|Low/dirty| I21[Service/flush ATF]
  I20 -->|Normal| I22[Scan for tranny slip codes or test clutch]
  I22 -->|Tranny solenoid| I23[Inspect transmission solenoids]
  I22 -->|Mechanical| I24[Consider rebuild/replacement]

---

## deep-research-report-diagnostics.md:65

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault symptoms (transmission slip), diagnostic steps (check fluid, scan codes, pressure test), and repair ranges, which aligns with fault-finding and diagnostic reasoning.

```

**transmission_slip**: *Summary*: Excessive clutch slipping shows as high engine RPM with low vehicle speed under load. Check the transmission fluid (dirty or low fluid can cause slippage). Also scan for any transmission codes (e.g. torque converter clutch solenoid faults). A pressure test on the transmission may be required. Fix ranges from simple fluid/solenoid replacement to a rebuild if clutch packs are worn.  

## Summary

---

## deep-research-report-diagnostics.md:66

**Category:** `automotive_diagnostics`  
**Reason:** The text describes systematic fault-finding procedures, symptom-to-cause reasoning, diagnostic steps, tables comparing faults, and flowcharts for troubleshooting engine issues, which aligns with the diagnostics category.

## Summary

Modern engine diagnosis relies on reading live data from the ECU (fuel trims, sensor voltages, etc.) and following systematic checks. This guide defined each PID, its normal behavior, and common fault modes, and then applied them to 31 specific failure scenarios. For example, a vacuum leak is indicated by high positive fuel trims at idle and is diagnosed with smoke or soapy water tests, while a bad MAF shows similar trims but normal MAP, pointing to sensor cleaning or replacement. Tables were provided to quickly compare faults, and Mermaid flowcharts offer step-by-step diagnostic logic. Always start with easy checks (fluids, battery/voltage, visual inspection), use the scan tool data to narrow suspects, and confirm with targeted tests (pressure gauges, oscilloscopes, sensor swap, etc.). The cited references below reflect industry best practices and standards to aid technicians in systematic troubleshooting.

---

## deep-research-report-diagnostics.md:67

**Category:** `automotive_diagnostics`  
**Reason:** The source file is a deep‑research report focused on diagnostic techniques, OBD‑II data analysis, fault signatures, and professional diagnostic workflows, which aligns with the automotive_diagnostics category.

**Sources:** Authoritative automotive diagnostics references and industry guides were used, including Motor’s OBD-II data analysis, sensor operation definitions, and technical articles on fuel systems and sensors, plus best-practice tips from professional mechanic forums.

---

## deep-research-report-fault-reference.md:0

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt defines OBD-II PIDs, their measurements, normal ranges, and how they behave under faults – core concepts about sensor data and baseline ranges, which falls under automotive fundamentals.

# Automotive OBD-II PIDs & Fault Reference

**Executive Summary:** This reference sheet explains key OBD-II parameter IDs (PIDs) – what they measure, normal ranges, failure modes – and how they change under common faults (lean/rich fuel mixtures, sensor failures, mechanical issues, etc.). It then summarizes 31 simulated fault profiles (e.g. vacuum leak, dirty MAF, ignition misfires, cooling problems, etc.), highlighting their signature scan-tool readings, likely causes, and step-by-step diagnostic actions. Tables map each fault to its symptoms, causes, and recommended next steps. Practical tips on live-data interpretation, test procedures, and safety are also provided. 

## Key PID Definitions & Normal Ranges

---

## deep-research-report-fault-reference.md:1

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt describes core sensor signals (RPM, vehicle speed, MAP), their normal ranges, how they are calculated and used for engine load, which are fundamental concepts about sensor operation and baseline ranges rather than fault diagnosis or other automotive topics.

- **Engine RPM:** Crankshaft speed in revolutions per minute. Normal idle ~700–900 rpm; WOT (wide-open throttle) ~3000–4000 rpm or higher.  
- **Vehicle Speed:** Road speed (km/h or mph) from wheel/transmission sensors. Zero at idle, increases with throttle.  
- **Calculated Engine Load:** Normalized engine load (%) based on airflow (percent of max torque). ~30–50% at idle on NA engines; reaches 100% at WOT. Calculated from MAP, MAF and barometer.  
- **Intake Manifold Pressure (MAP, kPa or inHg):** Pressure in intake manifold. At idle, high vacuum (~20–30 inHg); at WOT it approaches atmospheric (0–10 inHg vacuum). PCM uses MAP for load and fueling. A stuck-open throttle or vacuum leak skews MAP (higher than expected vacuum).

---

## deep-research-report-fault-reference.md:2

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt discusses sensor readings, abnormal values, and how faults in MAF, IAT, ECT, and TPS affect engine operation and diagnostics, which aligns with fault-finding and diagnostic reasoning rather than core concepts or generic automotive info.

- **Mass Air Flow (MAF, g/s or lb/min):** Air mass entering engine. Idle ~2–7 g/s; at moderate cruising (~2500 rpm) ~15–25 g/s. Dirty or failing MAF gives **lower** readings for a given RPM. Check MAF accuracy with a scan tool or meter, compare against known specs.  
- **Intake Air Temp (IAT, °C/°F):** Air temperature entering engine. Normal ~ ambient. Implausible IAT (e.g. –40°C) means sensor shorted. A stuck-cold IAT makes PCM over-fuel (rich trim).  
- **Engine Coolant Temp (ECT, °C/°F):** Coolant/engine temp. Should warm up to ~90–100°C (190–212°F). Stuck-open thermostat yields ~60–70°C after warm-up (long run time). Stuck-closed thermostat yields ~110°C (overheat).  
- **Throttle Position (TPS, %):** Throttle plate angle (0% closed, 100% wide open). Correlates with engine load. Stuck TPS (e.g. locked at ~12%) shows no change with pedal movement.

---

## deep-research-report-fault-reference.md:3

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains basic OBD-II sensor behavior (oxygen sensors), voltage ranges, and fuel trim concepts (STFT/LTFT) with normal operating ranges, which are core fundamentals of automotive diagnostics.

- **Oxygen Sensors (O₂ B1S1/2, V or λ):** Measure exhaust O₂. Bank1 Sensor1 (upstream pre-cat) swings 0.1–0.9 V as mixture oscillates; B1S2 (downstream) should be steady ~0.4–0.6 V when cat is good. Wideband “WR” (voltage or λ) sensors output a linear voltage or ratio ~0.0–5.0 V (some scanners label this). Fault: O₂ stuck high/low means sensor dead; upstream and downstream sensors tracking suggests a bad catalytic converter.  
- **Short-Term Fuel Trim (STFT, Bank1):** Immediate fuel correction (%). Normal ~–10% to +10%. *Positive* STFT (e.g. +10–+20%) = PCM adding fuel to fix a lean condition. *Negative* STFT means removing fuel (rich condition).  
- **Long-Term Fuel Trim (LTFT, Bank1):** Averaged (long-term) fuel correction. Should return near 0% at steady state, but ±5–8% is common. LTFT beyond ±10% indicates a persistent issue.

---

## deep-research-report-fault-reference.md:4

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes fault signatures, symptom-to-cause reasoning, and diagnostic interpretation of sensor data (catalyst temperature, ignition timing, battery voltage, EVAP purge command) to identify potential issues such as clogged catalyst, timing-chain problems, alternator/regulator faults, and EVAP system malfunction. This aligns with the diagnostic focus of the automotive_diagnostics category.

- **Catalyst Temp (B1S1, °C):** Exhaust gas temperature at catalytic converter inlet (via sensor in B1S1). Typical idle temps ~300–600°C, at full load can exceed 800°C. High temp at constant RPM/gear indicates a clogged catalyst. (OBD PID 0x3C; -40 offset).  
- **Ignition Timing Advance (Spark Adv, °):** Timing in degrees before TDC. Typically 10–30° at idle, up to ~40° under light cruise. Retarded/low advance (e.g. 0°–10° at cruise) suggests timing-chain/chain-stretch or cam/crank sync issue.  
- **Control Module Voltage (Battery, V):** Vehicle electrical system voltage (0–65.535 V range). Normal ~13.8–14.5 V when charging. ~12.7 V running = weak alternator; ≥15.5 V = overcharging/regulator fault.  
- **EVAP Purge Command (%):** Purge valve duty (0% off, 100% on). Normally 0% at idle; if stuck at 100% at idle, PCM floods intake with fuel vapor (lean idle lean mixture).

---

## deep-research-report-fault-reference.md:5

**Category:** `automotive_diagnostics`  
**Reason:** The snippet describes a specific fault condition (EGR valve stuck at 100% causing misfire/rough idle) and explains the diagnostic implication, which fits the fault‑finding focus of the automotive_diagnostics category rather than general fundamentals or unrelated automotive information.

- **EGR Command (%):** EGR valve duty (0% closed, 100% fully open). Normally 0% at idle and low load; if stuck at 100%, large EGR flow causes misfire/rough idle.

---

## deep-research-report-fault-reference.md:6

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains normal sensor ranges, how measurements are taken, sensor types, and OBD-II PID reporting—core concepts of automotive fundamentals.

_Normal Ranges:_ STFT/LTFT typically ±10% (see above). Normal idle RPM ~750 ±100. Normal coolant ~90°C (190°F). O₂ voltage oscillates ~0.1–0.9 V quickly in closed-loop. Normal IAT ~ambient. MAF varies by engine size (see above).  

**How Measured:** The PCM reads sensors (thermistors, pressure sensors, Hall/crank sensors, etc.) and reports via OBD-II PIDs. For example, MAF often uses a hot-wire or hot-film sensor output (g/s); MAP uses a piezo or silicon sensor (kPa); TPS often a potentiometer (voltage). Engine load is calculated from MAP/MAF. O₂ sensors (zirconia or wideband) output voltage or current proportional to O₂ content.

---

## deep-research-report-fault-reference.md:7

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific sensor failure modes, their symptoms, and diagnostic implications, focusing on fault signatures and cause‑effect reasoning rather than basic concepts or unrelated automotive info.

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

---

## deep-research-report-fault-reference.md:8

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt discusses PID fault symptoms, correlations, and recurring PID themes, focusing on core concepts of PIDs, sensor behavior, and baseline ranges—key fundamentals of automotive diagnostics.

Each PID’s **fault symptom** on live data often correlates to these: e.g. lean (vacuum leak) → STFT↑, MAF↓, idle↑; rich (injector leak) → STFT↓ (negative); O₂ stuck → flat-line voltage; EGR stuck → EGR% 100%, RPM bouncing; etc.

## Recurring PID Themes

These are common patterns seen in multiple faults:

---

## deep-research-report-fault-reference.md:9

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses fault signatures, compensation values, and diagnostic interpretation of sensor readings to identify engine issues.

- **Lean Compensation:** STFT/LTFT **positive** (often +6% to +20%) – PCM adding fuel. Indicates a lean mixture (vacuum leak, low fuel, clogged filter, dirty MAF, etc.). Idle may be high (1500+ rpm) if too much unmetered air. 
- **Rich Compensation:** STFT/LTFT **negative** (e.g. –10% to –18%) – PCM removing fuel. Causes: leaking injector, high fuel pressure, faulty fuel pressure regulator, stuck-rich sensor. 
- **Low MAF Readings:** MAF (g/s) abnormally **low** for given RPM/load (e.g. 12–22 g/s when more expected). Root: dirty/failed MAF, air bypass (intake leak, hole). Check linearity by graphing MAF vs RPM. 
- **High Throttle, Low Output:** Throttle position high (e.g. 60–75%), but engine load (MAF, Torque) low. Often from low compression (one cylinder misfire) or mechanical drag. Check compression test and ignition.

---

## deep-research-report-fault-reference.md:10

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific fault signatures, symptoms, and diagnostic steps for various engine issues (vacuum leak, load-only lean, idle instability, EGR stuck open), focusing on interpreting sensor data and fault codes to identify root causes. This aligns with automotive diagnostics rather than fundamentals or other automotive information.

- **Unmetered Air / Vacuum Leak:** Idle lean: STFT/LTFT jumps high, MAF low, intake pressure ~high vacuum, idle RPM ~500–1500. Classic pattern: pronounced high trims + high idle. Confirm with smoke test or by covering vacuum ports.  
- **Load-only Lean:** Normal trims at idle but STFT ~+20%, LTFT +15% under high load (full throttle). Possible weak fuel pump or injector; fuel pressure drops under demand. Check fuel pressure, pump flow. 
- **Idle Instability:** RPM bouncing 500–1500, O₂B1S2 oscillating. Likely misfire or severe vacuum leak. Check misfire counters (DTC P030x), ignition coils, plug wires, and vacuum lines. 
- **EGR Stuck Open:** Commanded EGR 100% (flat), unstable/higher idle, mild positive trim. Root cause: EGR valve or solenoid stuck. Test by applying vacuum/power to EGR and listening.

---

## deep-research-report-fault-reference.md:11

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific fault conditions, symptom-to-cause analysis, and diagnostic steps for various vehicle issues (EVAP purge stuck, coolant temperature anomalies, O2 sensor behavior). This aligns with fault finding and diagnostic reasoning rather than core concepts or generic automotive information.

- **EVAP Purge Stuck:** EVAP purge command 100% at idle, with positive fuel trims (lean idle). Means purge solenoid stuck open dumping fuel vapor. Check by disabling purge valve (unplug coil) and watching idle. 
- **Coolant Too Cold:** ECT ~60–70°C after long run time, LTFT lean (PCM enriching for perceived cold). Likely stuck-open thermostat or low coolant. 
- **Overheating:** Coolant ≥102–112°C. Potential thermostat stuck closed, fan fault, or coolant level. At idle (speed 0) exclusive: fan relay or sensor issue. 
- **Unstable Coolant:** ECT fluctuates wildly 77–110°C. Air pocket or failing sensor. Check gauge vs scanner, bleed system. 
- **O₂ Oscillating (Bad Cat):** O₂ B1S2 (downstream) oscillates (voltage swings) nearly matching upstream O₂S1. Indicates cat not absorbing O₂ (degraded). 
- **O₂ Stuck:** B1S2 flat 0 V or pegged high (0.9 V). Indicates open/shorted O₂ sensor circuit.

---

## deep-research-report-fault-reference.md:12

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific fault symptoms and diagnostic interpretations (e.g., O₂ sensor stuck, IAT implausible, sensor failures, voltage issues) and suggests diagnostic steps, which aligns with the automotive_diagnostics category.

- **O₂ Stuck:** B1S2 flat 0 V or pegged high (0.9 V). Indicates open/shorted O₂ sensor circuit. 
- **O₂ Drift:** Downstream flat around mid-level ± small swing; LTFT slowly increases. Cat likely working but upstream or fueling is drifting lean. Replace O₂ or check mixture. 
- **IAT Implausible:** IAT reads –40°C (0x00). Sensor open/short. Results in rich trim (PCM thinks very cold air). 
- **ECT Sensor Dead:** ECT –40°C, rich STFT (–10%). False cold reading causes over-rich compensation. 
- **MAP Mismatch:** High RPM (~3000) + moderate throttle, but MAP reading stays like idle (high vacuum). Could be MAP sensor fault or shorted vacuum line.  
- **TPS Stuck:** TPS fixed (~12%) while RPM varies. Pedal and RPM decoupled. Swap or calibrate TPS. 
- **Low Battery Voltage:** Control module ~12.7 V during run. Weak alternator/battery.  
- **High Voltage:** ~15.8 V on run. Overcharging/regulator stuck.

---

## deep-research-report-fault-reference.md:13

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific fault signatures, symptom-to-cause analysis, and diagnostic steps for various vehicle issues (e.g., high voltage, catalyst restriction, timing off, RPM vs speed mismatch). This aligns with the 'automotive_diagnostics' category, which covers fault finding, diagnostic reasoning, and symptom interpretation.

- **High Voltage:** ~15.8 V on run. Overcharging/regulator stuck.  
- **Catalyst Restriction:** High engine load (e.g. 90%), low MAF flow, normal RPM/speed, **Cat Temp rising**. Choked exhaust. Measure backpressure or inspect cat. 
- **Timing Off:** Timing advance abnormally low (e.g. 0–10° at cruise), LTFT +. Late timing causes poor power. Likely cam/crank sync. Use timing light or scan cam/crank sync. 
- **RPM vs Speed Mismatch:** RPM high (4000+) but vehicle speed low (~25 km/h) at moderate load. Indicates transmission slipping or torque converter lock-up failure.

---

## deep-research-report-fault-reference.md:14

**Category:** `automotive_diagnostics`  
**Reason:** The file contains simulated fault signatures and diagnostic information, which falls under fault finding and diagnostic reasoning.

## Fault Profiles & Diagnostics

Below are the 31 simulated fault signatures with diagnostics:

---

## deep-research-report-fault-reference.md:15

**Category:** `automotive_diagnostics`  
**Reason:** The snippet provides a fault code, associated PID overrides, likely causes, and a step‑by‑step diagnostic procedure for locating and fixing a vacuum leak, which is characteristic of fault‑finding/diagnostic content rather than core concepts or generic automotive info.

| **Fault**                  | **Key PIDs** (overridden values)                           | **Likely Causes**                           | **Diagnostic Steps**                                                                                      | **Action**                             |
|----------------------------|------------------------------------------------------------|---------------------------------------------|-----------------------------------------------------------------------------------------------------------|----------------------------------------|
| **vacuum_leak**            | STFT +20%, LTFT +15%, MAF 12 g/s, Intake Pressure low, RPM 950, Speed 0 | Intake vacuum leak (hose, gasket), unmetered air | Listen/pressure-test intake for leaks; smoke-test system; block off hoses to isolate; check MAF (cover air tube). Expect idle drop when large leak closed. | Seal leak, retest trims.               |

---

## deep-research-report-fault-reference.md:16

**Category:** `automotive_diagnostics`  
**Reason:** The file contains fault signatures, DTC meanings, symptom-to-cause reasoning, diagnostic steps, and repair procedures, which are characteristic of automotive diagnostics.

| **dirty_maf**              | RPM 2500, Load ~50%, MAF 16 g/s, STFT +12%, LTFT +10%, Speed ~50 km/h | Contaminated MAF element, wrong airflow | Inspect/clean MAF sensor with cleaner; compare MAF vs RPM (should rise linearly). Swap in known-good. | Replace/clean MAF if out of spec.      |
| **air_filter_restriction** | Throttle ~63%, MAF 35 g/s, Load ~27%, RPM 2200, Speed ~35 km/h   | Severe intake restriction (blocked filter)  | Inspect air filter; measure MAF vs throttle. Filter clogged yields high throttle% for low airflow.   | Replace air filter.                    |
| **egr_stuck_open**         | Commanded EGR 100%, RPM fluctuating 600–1100, STFT +8%, Speed 0   | EGR valve/solenoid stuck open              | With engine off, measure vacuum/power on EGR – should move plate. At idle, suck on EGR vacuum line: engine should stumble. | Fix/replace EGR valve; clear codes.    |

---

## deep-research-report-fault-reference.md:17

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes fault symptoms, diagnostic tests, and remediation steps for fuel system issues, which aligns with fault-finding and diagnostic reasoning rather than core concepts or generic automotive info.

| **fuel_pump_weak_load**    | (Normal idle), but under load: RPM 4500, Speed 90 km/h, STFT +20%, LTFT +15% | Low fuel pressure under demand            | Perform fuel pressure test at idle and under WOT. Check pump flow. Under load trimming lean = pump or filter. | Replace fuel pump/filter.             |
| **dirty_injectors**        | STFT +14%, LTFT +11%, RPM wobble 1100–1350 (misfire feel)      | Clogged injectors, poor spray pattern      | Check scan misfire counters; swap injectors cylinder-to-cylinder – misfire should follow. Ultrasonic clean injectors. | Clean or replace injectors.           |
| **injector_leak**          | STFT −18%, LTFT −12% (rich trims)                           | Leaking injector(s)                        | Idle fuel pressure test (bleed). Cylinder balance test: introduce known vacuum leak to see cylinder output; leak injector overflows. | Replace leaking injector.             |

---

## deep-research-report-fault-reference.md:18

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures, symptom patterns, and diagnostic steps for specific component failures (injector stuck closed, ignition coil failure, spark plug wear), which aligns with fault-finding and diagnostic reasoning rather than core concepts or generic automotive info.

| **injector_stuck_closed**  | STFT +16%, LTFT +8%, RPM 750–1250 (idle hunt), Speed 0        | Injector stuck shut (fuel starvation)      | Scan for misfire on specific cylinder; swap injector or connector. Bypass injector control and gauge output. | Replace failed injector.             |
| **ignition_coil_failure**  | RPM 500–1500 random, O₂ B1S2 random swing, STFT +6%, Speed 0   | Failed coil (misfire on one or more cylinders) | Use a spark tester or oscilloscope to verify coil output. Swap coil to new cylinder to see if misfire follows.   | Replace faulty coil; check plugs.     |
| **spark_plug_wear**        | LTFT +9%, STFT +6% (slow rise, no RPM noise)                | Aged plugs, increased gap                 | Inspect spark plugs for wear/gapping. Check spark intensity. On-spark test at idle vs baseline.    | Replace spark plugs.                   |

---

## deep-research-report-fault-reference.md:19

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures, symptom-to-cause reasoning, and diagnostic steps for thermostat and cooling fan failures, which aligns with automotive diagnostics.

| **thermostat_stuck_open**  | ECT ~65°C after long run time (0x0E10 sec), >> Low temp    | Thermostat failed open                    | Verify with IR thermometer or scan tool: block heater to warm to ~90°C; if never reached, suspect thermostat. | Replace thermostat.                  |
| **thermostat_stuck_closed**| Coolant 112°C at speed ~25 km/h (overheat in motion)       | Thermostat failed closed                  | Monitor ECT while running; if rising uncontrolled, check hoses for heat. Feel upper hose (cold = stuck closed). | Replace thermostat; flush if needed.  |
| **cooling_fan_failure_idle**| Coolant 108°C at speed 0, RPM 750 (idle overheat only)   | Electric fan not running at idle           | With engine hot (~100°C), turn on A/C (if on same fan circuit) to test fan. Check fan relay, fuse, temp switch.  | Repair fan circuit; reset after cool. |

---

## deep-research-report-fault-reference.md:20

**Category:** `automotive_diagnostics`  
**Reason:** The source file contains multiple fault descriptions, diagnostic steps, and symptom-to-cause reasoning for water pump degradation, low coolant, and catalyst degradation, which aligns with fault-finding and diagnostic workflows rather than core concepts or generic automotive information.

| **water_pump_degradation** | RPM 3800, Load ~75%, Coolant 102°C (temp rises under load) | Worn impeller or pump failure             | Pressure test cooling system for leaks. Run engine at high RPM and watch ECT; if rises quickly under load, pump issue.  | Replace water pump; refill coolant.   |
| **low_coolant**           | Coolant 77–110°C fluctuating wildly (high SD)              | Air pocket or low coolant level           | Check coolant level; pressure-test for leaks; bleed system. Fluctuating temp often air in housing or failing sensor. | Refill/bleed coolant; replace sensor. |
| **catalyst_degradation**  | O₂ B1S1 & B1S2 both oscillating (random), WR voltage random | Catalytic converter failed (no O₂ buffering) | Measure downstream O₂ vs upstream: if both swing similarly, cat is bad. Perform catalyst efficiency test. | Replace catalytic converter.          |

---

## deep-research-report-fault-reference.md:21

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes specific fault codes, symptoms, diagnostic steps, and repair actions, which aligns with fault-finding and diagnostic reasoning rather than core concepts or general automotive info.

| **catalyst_restriction**  | Load ~94%, MAF 28 g/s (low), RPM 2800, Speed 40 km/h, Cat Temp ↑ | Clogged/partial cat/exhaust restriction  | Use an exhaust back-pressure gauge. Check turbo wastegate (if turbo). Inspect cat physically. | Repair/replace exhaust/catalyst.      |
| **evap_purge_stuck_open** | Purge 100%, STFT +14%, LTFT +6%, Speed 0 (lean idle)        | Purge solenoid stuck open                 | At idle, disconnect EVAP purge connector: idle should change. With key on, test solenoid coil to chassis (should be open). | Replace purge solenoid.              |
| **o2_sensor_drift**       | LTFT +10%, O₂ B1S2 ~flat (±5 mV around mid)              | Aging O₂ sensor (slow response)           | Wiggle test sensor wiring; check heater circuit. Swap downstream sensor to see if problem follows.  | Replace aging O₂ sensor.             |

---

## deep-research-report-fault-reference.md:22

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures, DTC meanings, symptom-to-cause reasoning, and diagnostic steps for O2 and IAT sensor failures, which falls under automotive diagnostics.

| **o2_sensor_failure_low** | O₂ B1S2 stuck at 0 V                                      | O₂ sensor open-circuit or disconnected    | Backprobe sensor: verify wiring and heater. If open, codes P0138/P0139 expected.  | Repair harness or replace sensor.    |
| **o2_sensor_failure_high**| O₂ B1S2 pinned high (0xC8/0.9V)                          | O₂ sensor shorted to voltage             | Similar to above: check wiring; if high, sensor may be shorted power.   | Replace sensor.                      |
| **iat_sensor_failure_cold**| IAT = −40°C (0x00)                                      | IAT sensor open (short to ground)        | Disconnect sensor: reading should go to ambient (~20°C). Short test sensor pins; replace if needed. | Replace IAT sensor.                  |

---

## deep-research-report-fault-reference.md:23

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific sensor failure modes, symptom patterns, and step‑by‑step diagnostic procedures (e.g., checking voltage, using a hand‑held vacuum sensor, interpreting DTCs). This is clearly fault‑finding/diagnostic content rather than general fundamentals or unrelated automotive information.

| **ect_sensor_failure**    | Coolant = −40°C, STFT −10% (rich trim)                    | ECT sensor open (short to ground)        | Same method: unplug ECT, sensor should return ambient. Code P0117. Replace sensor. | Replace ECT sensor.                 |
| **map_sensor_failure**    | RPM 3000, Throttle 44%, Intake Pressure idle-like (e.g. 0x95), MAF 45 g/s | MAP sensor or line failure           | Check MAP with hand-held vacuumsensor; apply vacuum and watch reading. Inspect/replace MAP.  | Replace MAP sensor/hoses.            |
| **tps_failure**          | Throttle stuck ~12%, RPM varies 900–2500 (TPS vs pedal mismatch) | Faulty TPS or throttle body           | Wiggle throttle, check pedal vs TPS voltages (or %). Use scan tool: see if TPS % moves with pedal.  | Replace/calibrate TPS (throttle body). |

---

## deep-research-report-fault-reference.md:24

**Category:** `automotive_diagnostics`  
**Reason:** The source file lists specific fault codes and provides symptom descriptions, measurement procedures, and repair actions, which is characteristic of diagnostic workflows rather than core concepts or generic automotive information.

| **alternator_failure**   | Control Module Voltage ~12.7 V (running), RPM 1100         | Alternator output weak                  | With A/C on and lights, measure voltage: should be ~14V. Test alternator output current. | Repair/replace alternator.          |
| **voltage_regulator_failure**| Voltage ~15.8 V (running)                              | Overcharging alternator/regulator       | Similar: measure with multimeter. If >14.8V, regulator bad.   | Replace voltage regulator/alternator. |
| **compression_loss**     | RPM 700–1300 unstable, Load ~19%, Throttle ~75%, MAF 22 g/s, STFT +10% | Low compression (worn rings/valves) | Perform relative compression test or use cylinder contribution. Compare to spec.  | Repair: rebuild head or engine.     |

---

## deep-research-report-fault-reference.md:25

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific fault signatures, symptom-to-cause reasoning, diagnostic steps, and repair actions for engine and transmission issues, fitting the diagnostics category.

| **head_gasket_leak**     | Coolant 95–115°C erratic, RPM 650–1200 (misfire), STFT +8% | Head gasket blown: coolant in cylinders | Use block tester (combustion gases in coolant); check for white smoke. Cylinder leak-down test.  | Replace head gasket / repair engine. |
| **timing_chain_stretch** | Timing advance low (e.g. 0x18 code), LTFT +7%, Load ~33%, RPM 2400, Speed 55 km/h | Advanced timing off (cam-crank out) | Use scan or cam-crank sync tests. On engines with variable timing, check cam sensor phasing. | Replace chain/tensioner; time engine. |
| **transmission_slip**    | RPM 4200, Speed ~25 km/h, Load ~56%                    | Transmission clutch slip                | Road test in safe area, check gear shifts. Monitor gear ratio PID vs actual RPM. Scan TCM codes. | Repair transmission (clutch, bands). |

---

## deep-research-report-fault-reference.md:26

**Category:** `automotive_diagnostics`  
**Reason:** The text outlines a step‑by‑step diagnostic workflow, including scanning codes, live data checks, visual inspections, sensor/actuator testing, functional tests, and engine tests, which aligns with fault‑finding and diagnostic procedures rather than core concepts or unrelated automotive info.

### Diagnostic Priority & Next Steps

1. **Scan for Codes:** Many faults set generic DTCs (P0171 lean, P0300 misfire, P0128 thermostat, P0420 cat, P0136 O₂ low, etc.). Use those for clues.  
2. **Live Data Checks:** Verify sensor readings vs reality. E.g. see if TPS moves with pedal, or MAF follows engine load.  
3. **Visual & Mechanical Inspection:** Hoses, wiring, connectors, vacuum leaks, damage. Check fluid levels and quality.  
4. **Sensor/Actuator Tests:** Use multimeter or oscilloscope: check O₂ heater, IAT/ECT resistances, MAP vac-press test.  
5. **Functional Tests:** Swap suspected parts if possible. Use hand-held vacuum on EGR, block EVAP purge, etc.  
6. **Engine Tests:** Compression/leak-down, timing light, fuel pressure gauge, injector balance. 

A simplified **diagnostic flow** for a lean/trim fault might be:

---

## deep-research-report-fault-reference.md:27

**Category:** `automotive_diagnostics`  
**Reason:** The text presents a step‑by‑step diagnostic flowchart for a lean/trim fault, describing symptom detection, possible causes, and systematic troubleshooting actions (e.g., checking MAF, vacuum leaks, fuel pressure, O₂ sensors). This matches the definition of automotive_diagnostics, which covers fault finding, symptom‑to‑cause reasoning, and diagnostic workflows.

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

---

## deep-research-report-fault-reference.md:28

**Category:** `automotive_diagnostics`  
**Reason:** The snippet describes a diagnostic flowchart, quick-test tips, and safety considerations for fault diagnosis, which aligns with fault-finding and diagnostic workflows rather than core concepts or general automotive information.

```

*(This flowchart is a guide: actual diagnosis may involve more steps.)*

## Quick-Test Tips & Safety

---

## deep-research-report-fault-reference.md:29

**Category:** `automotive_diagnostics`  
**Reason:** The passage provides step‑by‑step diagnostic procedures and symptom interpretation (e.g., checking fuel trims, O₂ sensor behavior, vacuum leak testing, ignition inspection, cooling system checks, battery/charging tests) which are core to automotive fault‑finding rather than general concepts or unrelated automotive info.

- **Fuel Trims:** Take readings at idle and at 2500–3000 rpm. Trims should stabilize near 0%. A *steady* high trim (+15%+) means a real lean condition. 
- **O₂ Sensors:** Use a scope or scan tool to see oscillation. A sluggish post-cat sensor with flat line suggests old converter.  
- **Vacuum Leaks:** Spray carb cleaner (or an unlit propane torch) around intake joints while watching RPM. A leak will cause RPM to rise. Always do this carefully (no open flame!).  
- **Ignition:** Check spark by pulling plug while cranking (ground side of boot). Also compare dwell/pulse width on coil drivers with scan tool if available.  
- **Cooling:** Never remove radiator cap when hot. Use IR thermometer to verify thermostat opening. Ensure coolant level in expansion tank is correct.  
- **Battery/Charging:** Test alternator output at 2000 rpm; verify voltage ~13.8–14.5 V. A battery drain/test isolate for parasitic draw if needed.

---

## deep-research-report-fault-reference.md:30

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt discusses basic sensor resistance values, OBD code tables, and expected resistance ranges for temperature sensors, which are core technical fundamentals of automotive systems rather than diagnostic procedures or broader automotive information.

- **Sensor Resistance:** Check IAT/ECT/MAP sensors off-vehicle with multimeter: e.g. at ~20°C, ECT should read ~2.5 kΩ (varies by make), IAT similar. OBD code tables (P0112, etc.) list the expected resistances.

---

## deep-research-report-fault-reference.md:31

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt discusses OBD-II PID specifications, freeze-frame data, sensor behavior, normal ranges, and references to official standards, which are core concepts of automotive fundamentals.

**Important:** Always ensure the engine is cool and ignition off before touching cooling system parts. When performing drive tests (e.g. transmission), follow safety guidelines (use stands, chocks). For EVAP/EGR tests, release vacuum slowly. Always disconnect battery when servicing electrical components.  

## References

- Official OBD-II PID specifications (SAE J1979)  
- Innova OBD freeze-frame PID definitions (engine sensor behavior and normal ranges)  
- ALLDATA Mass Air Flow Sensor Testing (normal MAF idle values)  
- MOTOR Magazine on Calculated Load (idle load norms)  
- CarParts.com on Catalyst Sensor (catalyst temperature monitoring)  
- Fuel Trim Theory (fuel trim interpretation)  

This sheet prioritizes OEM-standard terms and observations. All diagnostic steps should be confirmed against the specific vehicle’s service manual and in compliance with safety procedures.

---

## deep-research-report-fault-signatures.md:0

**Category:** `automotive_fundamentals`  
**Reason:** The chunk defines OBD-II sensors, PIDs, normal ranges, and explains fault signatures, which are core concepts of automotive fundamentals.

# Automotive PIDs, Sensors, and Fault Signatures – Definitions and Diagnostics

Modern vehicles report hundreds of real‐time parameters (PIDs) to the ECU (engine control unit). These include fuel trims, airflow, engine load, temperatures, voltages, etc. Understanding each PID and its normal range is key to diagnosing issues. Below we define common PIDs and sensors, explain fault “signatures” (patterns of PID readings), and outline typical problems and fixes.

## Key OBD-II Sensors and Parameters

---

## deep-research-report-fault-signatures.md:1

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains the meaning, behavior, and typical values of Short-Term and Long-Term Fuel Trim, which are core OBD-II concepts and fundamental automotive knowledge rather than diagnostic fault-finding or other automotive topics.

- **Short-Term Fuel Trim (STFT)** – Instantaneous fuel adjustment (%) by the ECU. Positive STFT (e.g. +6% to +20%) means the ECU is **adding fuel** to correct a lean mix; negative (e.g. –10% to –18%) means it’s **subtracting fuel** for a rich mix. Short-term trims update rapidly (milliseconds) based on O₂ sensor feedback. Typical STFT at steady idle is near 0% (±10% normal).
- **Long-Term Fuel Trim (LTFT)** – Slower, learned fuel adjustment (%) averaged over time. A consistent +10% STFT will usually shift into LTFT (and STFT resets to 0) on many ECUs. LTFT also aims for 0% over time; values above ~10% (either lean or rich) indicate underlying issues. Positive LTFT means ECU has permanently added fuel (lean condition), negative means fuel removed (rich condition).

---

## deep-research-report-fault-signatures.md:2

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes fault signatures and symptom-to-cause reasoning for MAF and TPS sensors, explaining how abnormal readings affect ECU behavior and driveability, which aligns with diagnostic analysis rather than pure fundamentals or generic automotive info.

- **Mass Air Flow (MAF) Sensor** – Measures the mass rate of intake air (g/s) entering the engine. The ECU uses MAF (often with Intake Air Temp) to compute correct fuel quantity. A low MAF reading for a given RPM/load (“MAF undervalued”) suggests the engine isn’t sensing enough air – the ECU will see this as lean and add fuel. MAF output is typically 0–5.0 V or PWM, corresponding to 0–655 g/s (for PID definitions). 
- **Throttle Position Sensor (TPS)** – Monitors the throttle plate angle (0–100%). The TPS (usually a potentiometer or Hall sensor on the throttle shaft) tells the ECU how far the driver is pressing the gas pedal. A correct TPS reading rises smoothly from closed to wide-open. A *stuck* TPS (fixed at ~12% or so) will decouple pedal input from engine response, causing driveability issues.

---

## deep-research-report-fault-signatures.md:3

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains sensor operation, normal ranges, and how ECU uses MAP and ECT data, focusing on core concepts and healthy baselines rather than diagnostic procedures.

- **Manifold Absolute Pressure (MAP) Sensor** – Measures absolute intake manifold pressure (0–255 kPa). The ECU uses MAP (with IAT and RPM) to compute air density and engine load via the speed-density method. A normal naturally-aspirated engine sees low pressure (high vacuum) at idle and near-atmospheric at full throttle; turbo engines use MAP pre- and post-turbo. A “MAP mismatch” (e.g. idle pressure at high RPM) indicates a faulty MAP or wiring.
- **Engine Coolant Temperature (ECT) Sensor** – Monitors coolant/engine temperature. This thermistor input lets the ECU know engine warm-up status. A typical operating ECT is ~85–95 °C; a reading stuck at –40 °C (often 0x00 byte) means the sensor is disconnected or failed (an “ECT sensor dead” fault). The ECU treats a –40°C reading as extreme cold, causing a rich mixture and no fan control.

---

## deep-research-report-fault-signatures.md:4

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains the operation, measurement ranges, and normal behavior of IAT and O₂ sensors, including how they affect mixture calculations and what failure modes look like. This is core sensor fundamentals rather than a step‑by‑step diagnostic workflow or fault‑signature analysis.

- **Intake Air Temperature (IAT) Sensor** – Measures intake air temperature (–40 to +215 °C). This affects air density; colder air is denser and requires more fuel. A failed IAT reading of –40 °C (0x00) falsely signals very cold intake. ECUs rely on IAT for mixture calculation. A stuck –40°C IAT (“IAT implausible”) can cause over‐fueling.
- **Oxygen (O₂) Sensors** – Monitor O₂ in exhaust, typically 0–1 V (narrowband) or current/λ (wideband). Upstream sensors (Bank1 Sensor1, etc.) feed the ECU to adjust fuel in closed-loop; ~0.45 V is stoichiometric, higher (~0.9 V) means rich, lower (~0.1–0.2 V) means lean. Downstream (post-cat) sensors measure catalyst efficiency (should stay ~0.6–0.7 V steady if cat is good). A *dead* O₂ sensor flatlines at 0 V or max, while a *sluggish* sensor drifts slowly, skewing fuel trims.

---

## deep-research-report-fault-signatures.md:5

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt describes basic OBD parameters (catalyst temperature, RPM, vehicle speed, calculated load) and explains their normal ranges and significance, which are core concepts of automotive fundamentals.

- **Catalytic Converter Temperature** – Many vehicles have thermistors on the catalyst substrate. Typical values can be very high (>800 °C in normal operation). Extremely high catalyst temperature indicates a clogged or overheating converter (“cat restriction”).
- **Engine RPM (Speed)** – Revolutions per minute of crankshaft. In a healthy engine, RPM correlates with throttle and load. Random RPM swings (e.g. 500–1500 rpm at idle) indicate misfire or vacuum issues.
- **Vehicle Speed** – Output from the speed sensor (0–255 km/h). A mismatch (e.g. high RPM with low speed) can hint at transmission slip or gear issues.
- **Engine Load (Calculated Load)** – A computed value (0–100%) indicating how much engine capacity is being used, often derived from MAF or MAP. Roughly, 100% load means full-throttle maximum torque. At idle, load may be ~10–30%. Calculated load is essentially “percent of peak torque”.

---

## deep-research-report-fault-signatures.md:6

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt discusses interpreting battery/module voltage readings, distinguishing normal vs. low/high voltage conditions, and linking them to fault signatures and OBD PID $42, which is diagnostic fault-finding information.

- **Battery/Module Voltage** – The ECU’s supply voltage (0–65.535 V range, but realistically ~10–20 V). Normally around 13.8–14.5 V with engine running. A reading ~12.7 V (“low voltage”) means undercharging or heavy load; ~15.8 V (“high voltage”) means overcharging/failed regulator. In OBD, PID $42 reports this voltage.

---

## deep-research-report-fault-signatures.md:7

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains standard OBD-II PIDs, formulas, units, and references SAE J1979, focusing on core concepts like encoding, ranges, and sensor data—characteristic of automotive fundamentals rather than diagnostic fault-finding or other automotive topics.

Each PID above has a standard OBD-II code and formula (see SAE J1979). For example, PID 06/07 are STFT/LTFT, 0C is RPM, 0D is speed, 0F is IAT, 10 is MAF, 11 is throttle position, etc.  All values quoted (ranges, units) come from the OBD-II specification.

## Fuel Trim & Air/Fuel System Faults

---

## deep-research-report-fault-signatures.md:8

**Category:** `automotive_diagnostics`  
**Reason:** The text explains fault signatures, fuel trim behavior, and how specific sensor faults (e.g., MAF undervaluation) cause observable diagnostic symptoms, which is characteristic of diagnostic reasoning rather than core concepts or generic automotive info.

- **Lean Compensation (positive fuel trim)** – High positive STFT/LTFT (e.g. +10% or more) means the ECU is *adding fuel* because it sees a lean mixture. Common causes: vacuum leaks (unmetered air), MAF under-reporting, weak fuel pressure, or exhaust leaks. For example, a vacuum leak at idle causes excessive air (high vacuum, high RPM) and the ECU adds fuel, showing +20% STFT.
- **Rich Compensation (negative fuel trim)** – Negative trims (e.g. –10%) mean ECU is *subtracting fuel* because the mixture is too rich. Causes include leaking injectors, too high fuel pressure, or IAT reading too cold.
- **MAF Undervalued** – If the MAF sensor reads lower than actual airflow, the engine is actually running lean but ECU thinks little air entered, so it adds fuel (STFT +). In data, this shows a low MAF reading (g/s) for given RPM/load. For example, at 2500 rpm a healthy MAF might be ~25–30 g/s, but a faulty MAF might show only ~16 g/s, causing +12% trims (see “dirty_maf” fault).

---

## deep-research-report-fault-signatures.md:9

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific fault signatures, symptom-to-cause relationships, and diagnostic interpretation of sensor data (e.g., throttle position, MAF, fuel trims) which aligns with automotive diagnostics.

- **Air Filter / Intake Restriction** – A clogged filter or intake restriction forces the throttle to open further to maintain power. Diagnostic signature: high throttle position (%) (~60–75%) with **low** MAF and engine load, and sluggish acceleration. The ECU enriches to compensate (positive trims). E.g. “air_filter_restriction” fault holds throttle ~63% while MAF is only ~35 g/s (low flow), engine load low.
- **Unmetered Air Leak (Vacuum Leak)** – Large vacuum leak causes excess airflow not measured by MAF. At idle this yields high vacuum (low intake pressure reading) and high idle RPM. The ECU sees a lean condition and adds fuel (STFT/LTFT sharply +), even though throttle is closed. The table’s “vacuum_leak” example shows STFT +20%, LTFT +15%, MAF only 12 g/s at 950 RPM idle (engine runs faster than expected). Classic signs: high idle RPM and positive fuel trims.

---

## deep-research-report-fault-signatures.md:10

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures, symptom-to-cause reasoning, and diagnostic interpretation of EVAP purge valve and O2 sensor failures, which falls under automotive diagnostics.

- **EVAP Purge Valve Stuck Open** – The purge valve injects fuel vapors into intake. If it’s stuck open (valve commanded 100%), raw vapor floods the intake. At idle this creates a lean running (engine is flooded with extra fuel vapors), so trims go positive. Signature: purge duty cycle 100%, positive fuel trim (~+14% STFT), rough idle. Innova notes a stuck-open purge causes rough idle and flooding of engine.
- **O₂ Sensor Drift/Failure** – A slow or failing narrowband O₂ sensor will “stick” at ~0.45 V (no high/low swings), or output stuck 0 V or 1.0 V. A flatlined downstream O₂ (e.g. sensor “stuck” at 0 V or high) indicates sensor failure. A dead sensor causes the ECU to ignore it (running open-loop). If the downstream (post-cat) sensor behaves like upstream (oscillating ~0.1–0.9 V), the catalytic converter is likely bad. A properly working cat yields a steady downstream O₂ ~0.6–0.8 V.

---

## deep-research-report-fault-signatures.md:11

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes specific fault signatures, symptom-to-cause relationships, and diagnostic interpretation of sensor data (e.g., P0420, O₂ behavior, coolant temperature anomalies), which aligns with automotive diagnostics rather than core fundamentals or generic automotive information.

- **Catalyst Issues** – A failing catalytic converter often triggers a P0420 and causes the downstream O₂ to mirror the upstream. As one engineer noted, *“downstream O₂ oscillates at ~14.7 λ instead of staying flat,”* confirming a bad cat. Also, a physically restricted or collapsed converter causes backpressure: engine load high but MAF/flow low, and exhaust heat (cat temp) soars.
- **Engine Coolant Too Cold (Thermostat Stuck Open)** – If ECT stays around 60–65 °C long after start (and run time is long), the thermostat may be stuck open. The ECU thinks the engine is still warming up, so it might enrich fuel (cold idle is richer).
- **Overheating / Coolant Erratic** – If ECT reads very high (~105–112 °C) at idle or under load, overheating is occurring. High ECT alone may trigger codes (P0128 for low coolant temp too). Random fluctuating ECT (77–110 °C) suggests low coolant or air pockets.

---

## deep-research-report-fault-signatures.md:12

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures, symptom patterns, and diagnostic reasoning for ignition misfires, throttle position faults, and voltage issues, which is core to automotive diagnostics.

- **Ignition Misfires** – Irregular RPM (especially at idle) and oscillating O₂ readings often mean misfires. A failed coil or spark plug causes random dips in power: signature is “RPM random 500–1500, O₂ oscillating, positive trims” (ECU leans mixture due to misfires). Cars.com lists rough idle and stalling as EGR/fuel trim symptoms, but misfires also cause lean trims.
- **Throttle Position Faults** – If TPS is stuck (fixed signal) the ECU sees constant throttle angle. Example: “tps_failure” fault sets TPS ~12% (closed), but RPM jumps with no pedal input. This “pedal-RPM decoupling” signals TPS or wiring failure. Check if actual pedal vs TPS voltage diverge.
- **Electrical Voltage** – Low alternator output (~12.7 V) yields undercharging (P0562 code) and can cause erratic sensor readings. High voltage (~15.8 V) indicates overcharging/regulator failure (P0563). The ECU monitors “control module voltage” to catch these.

---

## deep-research-report-fault-signatures.md:13

**Category:** `automotive_diagnostics`  
**Reason:** The snippet discusses typical fault examples and fault signatures, which falls under fault finding and diagnostic reasoning.

## Typical Fault Examples

While dozens of faults exist, many break down into the above themes. Some representative cases:

---

## deep-research-report-fault-signatures.md:14

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes specific fault signatures, symptom-to-cause relationships, and diagnostic interpretations (e.g., lean conditions, injector issues, compression loss, alternator faults), which aligns with automotive diagnostics.

- **Fuel Pump Weak Under Load**: At high RPM/load (4500 RPM, ~90 km/h), STFT +20%, LTFT +15%. Normal idle. Indicates pump can’t deliver enough fuel, lean at high demand.
- **Dirty/Leaking Injectors**: Positive fuel trims and minor RPM wobble at idle. A leaking injector may cause rich condition (neg trim), while dirty injectors cause lean flags.
- **Compression Loss / Head Gasket Leak**: These cause both misfire and cooling issues. For instance, “head_gasket_leak” yields random RPM (misfire) plus erratic coolant temp (95–115 °C), as combustion gases enter coolant and also lean mixture (STFT +8%).
- **Alternator/Regulator Faults**: An alternator failing to maintain >14 V will show ~12.7 V at ~1100 RPM. Overvoltage shows ~15.8 V. These usually set P0562/P0563.

---

## deep-research-report-fault-signatures.md:15

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes specific fault signatures and diagnostic clues (timing off, transmission slip) and explains how to interpret them, which falls under fault-finding/diagnostic reasoning.

- **Timing Off (Ignition Delayed)**: Lower-than-normal ignition advance (e.g. ~10° vs 20° at part-throttle) gives slight sluggishness. The ECU sees less power at given RPM, so it may raise LTFT (e.g. +7%). Typical cruise RPM is lower; no obvious misfire code.
- **Transmission Slip**: High RPM (4200) with low vehicle speed (~25 km/h) and moderate load suggests slipping (engine revving but wheels not spinning proportionally). It won’t set an engine DTC, but the mismatch is a clue.

---

## deep-research-report-fault-signatures.md:16

**Category:** `automotive_diagnostics`  
**Reason:** The file discusses fault signatures, check-engine codes, and matching PID signatures to causes, which is diagnostic reasoning.

Each fault above usually sets relevant check-engine codes: e.g. lean/rich (P0171/2), misfires (P0300-P030x), sensor circuit faults (P0112 Low Coolant Temp, P0136 O₂ sensor slow, P0106 MAP range, etc.). When diagnosing, match the PID signature to common causes using the glossary terms below.

## Glossary of Terms

---

## deep-research-report-fault-signatures.md:17

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt explains core concepts such as fuel trim, AFR, lambda, and O₂ sensor roles, which are fundamental automotive knowledge rather than diagnostic procedures or other automotive information.

- **Adaptive Trims (Fuel Trim)** – Adjustments (%) made by the ECU to the injector pulse width. **Short-Term Fuel Trim (STFT)** reacts immediately to oxygen sensor readings; **Long-Term Fuel Trim (LTFT)** represents learned compensation over time. Positive trim = adding fuel (lean compensation); negative = removing fuel (rich compensation).
- **Air–Fuel Ratio (AFR) / Lambda (λ)** – Ratio of air mass to fuel mass. Stoichiometric λ=1 (≈14.7:1 for gasoline). Narrowband O₂ sensors switch ~0.45 V at stoich.
- **Bank and Sensor (O₂)** – Bank 1 is the side with cylinder 1; Sensor 1 is upstream (pre-cat), Sensor 2 is downstream (post-cat). Upstream sensors control fuel trim, downstream monitor catalyst.

---

## deep-research-report-fault-signatures.md:18

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault signatures and diagnostic behavior of various sensors and components, explaining how failures manifest and affect vehicle operation, which aligns with diagnostic reasoning rather than core fundamentals or unrelated automotive information.

- **Catalytic Converter (Cat)** – Emission control device that converts CO/HC to CO₂/H₂O. **Cat Restriction** (overheating/backpressure) chokes exhaust flow, reducing power and raising cat temp. **Catalyst Degradation** means the cat isn’t working; the downstream O₂ will oscillate like the upstream if the cat is bad.
- **ECT (Engine Coolant Temp) Sensor** – A thermistor in the cooling system. ECU uses ECT for engine warm-up fueling, fan control and gauge. A stuck-cold ECT (–40 °C reading) enriches the mixture as if cold.
- **IAT (Intake Air Temp) Sensor** – A thermistor measuring inlet air temperature. Used to adjust AFR for air density. Stuck reading (–40 °C or very high) skews fueling.
- **MAP (Manifold Absolute Pressure) Sensor** – Provides intake manifold pressure. Along with RPM and IAT, ECU uses MAP to compute engine load in speed-density engines. A “MAP mismatch” occurs if MAP doesn’t change as expected (e.g. showing idle vacuum at high RPM).

---

## deep-research-report-fault-signatures.md:19

**Category:** `automotive_diagnostics`  
**Reason:** The excerpt describes fault signatures and failure modes of various sensors (TPS, MAF, O₂, vacuum leak, EGR) and how they cause lean conditions and affect fuel trims, which is diagnostic information rather than core concepts or general automotive info.

- **TPS (Throttle Position Sensor)** – Monitors throttle plate opening. Allows the ECU to know driver demand. A stuck TPS breaks correlation between pedal and engine speed.
- **MAF (Mass Air Flow) Sensor** – Measures the mass rate (g/s) of incoming air. Crucial for fuel metering in MAF-based systems. If MAF reads low (due to dirt/failure), ECU will add fuel (lean condition).
- **O₂ Sensor (Narrowband)** – Electrochemical sensor output 0–1 V. Indicates rich/lean by voltage around 0.45 V (rich ≈0.8–0.9 V, lean ≈0.1–0.2 V).
- **Vacuum Leak** – Unmetered air entering the intake (e.g. cracked hose, stuck-open valve). Classic lean condition: high idle, high STFT/LTFT, low intake pressure reading.
- **EGR (Exhaust Gas Recirculation)** – Recycles a small portion of exhaust to the intake to reduce NOx. Normally opens only at cruise/part throttle. **Stuck-Open EGR** floods intake with exhaust: rough idle and lean fuel trims (ECU sees diluted air).

---

## deep-research-report-fault-signatures.md:20

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses fault signatures, DTC meanings, and how specific sensor behaviors (e.g., EVAP purge valve stuck open) cause specific diagnostic trouble codes and symptoms, which is core to automotive diagnostics.

- **EVAP Purge Valve** – Solenoid controlling fuel vapor (from charcoal canister) into intake. Normally closed at idle. If stuck open, excess vapors lean out idle (engine runs rich in terms of oxygen sensor reading, but actually flooded by fuel vapor) causing rough idle.
- **DTC (Diagnostic Trouble Code)** – Standard “P” codes (e.g. P0171: System Too Lean, Bank1; P0128: Coolant Thermostat Below Regulating Temperature; P0420: Catalyst Efficiency Below Threshold, etc.). Each PID fault signature often triggers specific DTCs (e.g. lean trim > a threshold, O₂ response slow, etc.).
- **Calculated Load** – Computed % (0–100%) of engine’s capacity (based on airflow). 100% at WOT. Useful to gauge engine effort. A normal idle load is engine/displacement dependent (see MOTOR article).
- **Battery Voltage / Alt. Output** – Normal charging voltage is ~13.8–14.5 V. ~12.7 V (engine running) is low (bad alternator), ~15.5–15.8 V is high (bad regulator). PID 42 returns this as a float (volts).

---

## deep-research-report-fault-signatures.md:21

**Category:** `automotive_diagnostics`  
**Reason:** The text describes a specific fault symptom (transmission slip) and its characteristics, which is diagnostic information rather than a core concept or general automotive info.

- **Transmission Slip** – In automatics, characterized by high engine RPM with disproportionately low vehicle speed (e.g. 4200 RPM @ 25 km/h). Feels like revving engine with no accelleration.

---

## deep-research-report-fault-signatures.md:22

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses fault signatures, matching observed PID anomalies to definitions, troubleshooting steps, and diagnostic reasoning, which aligns with automotive diagnostics.

Each term above is illustrated by the fault profiles. For example, the “vacuum_leak” fault shows high idle RPM and positive fuel trims (lean compensation); the “catalyst_degradation” fault shows oscillating downstream O₂. Troubleshooting involves matching observed PID anomalies (e.g. +STFT, low MAF, etc.) to these definitions and common causes.

**Sources:** Standard OBD-II definitions and automotive diagnostics guides. The above details synthesize industry knowledge (SAE J1979, manufacturer bulletins, and expert technical articles) with the specific fault patterns provided. Each diagnostic signature here is grounded in how ECUs use these sensors to maintain stoichiometry.

---

## deep-research-report-random-conversation.md:0

**Category:** `other_automotive_information`  
**Reason:** The file is a deep research report with an executive summary and appears to be a random conversation or project documentation, not covering core automotive fundamentals or diagnostic procedures.

# Executive Summary

---

## deep-research-report-random-conversation.md:1

**Category:** `automotive_fundamentals`  
**Reason:** The document provides a glossary of key automotive terms, describes basic to advanced maintenance tasks, outlines safety practices, tools, regulatory standards, and continuing‑education topics—all core concepts and foundational knowledge rather than fault‑finding or diagnostic procedures.

This report provides an authoritative overview of automotive maintenance fundamentals. It includes a concise **glossary of key terms and acronyms** (OEM, SAE, torque, ECU, OBD-II, etc.), with definitions and typical contexts. We describe **common maintenance tasks** at basic, intermediate, and advanced skill levels (with tools and step outlines). A section on **safety, tools, and diagnostic equipment** covers essential shop practices (PPE, multimeter, scan tool, torque wrench, lift, A/C service tools, etc.). We review **regulatory and certification standards** relevant to technicians: ASE certification (5-year recertification requirement), EPA Section 609 refrigerant certification, OSHA shop safety, and manufacturer training. Sample **continuing-education (CE) course topics** are suggested (hybrid/EV systems, advanced diagnostics, etc.) with example objectives and assessment methods. Finally, practical **recordkeeping and service-interval** advice is given (follow OEM schedules,

---

## deep-research-report-random-conversation.md:2

**Category:** `other_automotive_information`  
**Reason:** The snippet discusses practical recordkeeping, service-interval advice, OEM schedules, documentation, and customer communication—topics that are automotive-related but do not cover core technical fundamentals or diagnostic procedures.

Finally, practical **recordkeeping and service-interval** advice is given (follow OEM schedules, document all services) and tips on clear **customer communication**.

---

## deep-research-report-random-conversation.md:3

**Category:** `automotive_fundamentals`  
**Reason:** Defines core automotive terms and glossary, which are fundamental concepts.

## Core Terms and Glossary  
The table below defines core terms used in automotive maintenance. Context notes typical usage (e.g. in service manuals or technician conversations).

---

## deep-research-report-random-conversation.md:4

**Category:** `automotive_fundamentals`  
**Reason:** These entries define basic automotive terms and standards (OEM, SAE, torque) that are core concepts.

| Term                     | Definition                                                         | Context/Notes                                              |
|--------------------------|--------------------------------------------------------------------|------------------------------------------------------------|
| **OEM**                  | Original Equipment Manufacturer – the vehicle’s maker. OEM parts are genuine parts made by the automaker. | Distinguishes from aftermarket parts.                      |
| **SAE**                  | Society of Automotive Engineers – standards organization. Sets industry norms (e.g. oil viscosity grades like SAE 5W-30, diagnostic specs). | See SAE standards for oil, threads, scan tool PIDs.        |
| **Torque**               | Rotational force produced by an engine’s crankshaft. Measured in lb·ft or N·m. More torque means greater ability to do work. | Used in engine output ratings and when tightening bolts.   |

---

## deep-research-report-random-conversation.md:5

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt defines core engine concepts such as compression ratio, ignition timing, ECU, and OBD-II, which are fundamental automotive knowledge.

| **Compression Ratio**    | Ratio of cylinder volume at bottom-of-stroke to top-of-stroke.     | Higher ratio can yield more power (requires high-octane fuel). |
| **Ignition Timing**      | Moment when spark plug fires relative to piston position/crank angle (usually degrees before top dead center). | Adjusted (advanced/retarded) for performance, governed by ECU. |
| **ECU** (Engine/Elec. Control Unit) | The engine’s computer that controls fuel injection, ignition, idle, emissions, etc., by processing sensor data. | May also be called ECM/PCM; central to modern engine management. |
| **OBD-II**               | On-Board Diagnostics II – the standard vehicle self-diagnostic system (on all 1996+ cars in the U.S.). Provides trouble codes and live data via a 16-pin port. | Required by EPA/NHTSA for emissions control; scanned with a code reader. |

---

## deep-research-report-random-conversation.md:6

**Category:** `automotive_fundamentals`  
**Reason:** The text defines basic maintenance concepts and vehicle fluid/filter types, which are core automotive fundamentals.

| **Preventive Maintenance (PM)** | Scheduled maintenance (oil changes, filter replacements, inspections) to prevent breakdowns. | Follows manufacturer’s maintenance schedule.               |
| **Maintenance Schedule**  | List of manufacturer-recommended services by mileage/time.   | Found in owner’s manual; required for warranty coverage. |
| **Fluids**               | Key vehicle fluids: engine oil (lubrication), coolant/antifreeze (engine temp control), brake fluid (hydraulics), transmission fluid, power steering fluid, etc. | Use correct specifications (e.g. DOT ratings, viscosity).  |
| **Filters**              | Replaceable elements: oil filter (engine oil), air filter (engine intake), fuel filter, cabin-air filter. | Keep contaminants out; replaced per schedule or condition.  |

---

## deep-research-report-random-conversation.md:7

**Category:** `automotive_fundamentals`  
**Reason:** These are core engine components and their basic operating principles.

| **Serpentine Belt**      | Long, multi-rib belt that drives accessories (alternator, AC compressor, power steering pump, etc.). | Inspection for cracks/wear is routine; replacement requires loosening tensioner. |
| **Timing Belt/Chain**    | Belt or chain linking crankshaft to camshaft(s) to synchronize valve timing. | Critical engine component; replaced at OEM interval (often 60k–100k mi). |
| **Spark Plug**           | Ignition component that delivers a high-voltage spark to ignite the air-fuel mixture in each cylinder. | Replaced at service intervals; improper spark causes misfires. |
| **Fuel Injection**       | System that delivers fuel into engine cylinders or intake manifold via injectors. | Modern cars use electronic fuel injection (replaced carburetors). |
| **Turbocharger**         | Exhaust-driven forced-induction device that compresses intake air to produce more power. | Increases engine efficiency/power; commonly called a “turbo.” |

---

## deep-research-report-random-conversation.md:8

**Category:** `automotive_fundamentals`  
**Reason:** Describes core hybrid system components and key concepts like regenerative braking and SoC.

| **Regenerative Braking** | Energy-recovery braking system (on hybrids/EVs) that slows the vehicle by converting kinetic energy into electrical energy for storage. | Reduces wear on friction brakes; contributes to battery charging. |
| **Battery Management System (BMS)** | Electronic system that monitors and controls battery state (SoC, temperature, cell balance) in hybrid/EV vehicles. | Ensures safe charging/discharging and optimizes battery lifespan. |
| **State of Charge (SoC)**| Battery charge level (percentage of full capacity). | Key metric for EV/hybrid battery health and range estimation. |

---

## deep-research-report-random-conversation.md:9

**Category:** `automotive_fundamentals`  
**Reason:** The text describes basic maintenance tasks and required tools, which are core concepts of automotive fundamentals.

## Common Maintenance Tasks and Competency Levels  

- **Basic Tasks (Entry-Level):** These are routine services requiring basic tools (wrenches, screwdrivers, oil pan, etc.). Examples:
  - *Oil & Filter Change:* Drain old oil, replace oil filter, refill fresh oil to spec.  
  - *Fluid Checks:* Check and top off engine coolant, brake fluid, transmission fluid, power steering fluid, windshield washer fluid.  
  - *Tire Maintenance:* Check tire pressure, rotate tires every interval.  
  - *Basic Inspections:* Inspect belts, hoses, lights, wipers, battery voltage.  
  - *Spark Plug Replacement:* Remove and gap plugs (socket wrench and gap gauge).  
  - *OBD-II Scan:* Read/reset engine fault codes with a scan tool.  
  - *Basic Diagnostics:* Use a multimeter to check battery voltage and simple circuits.

---

## deep-research-report-random-conversation.md:10

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific repair procedures that require specialized tools and skills, focusing on fault-finding and step‑by‑step diagnostic service tasks.

- **Intermediate Tasks:** Require more skill and specialized tools (brake tools, jacks, torque wrenches, scan tools, A/C refrigerant gauges, etc.). Examples:
  - *Brake Service:* Lift vehicle, remove wheels, replace brake pads/shoes, inspect rotors/drums. Bleed brakes if fluid changed. (Tools: floor jack, brake tools, torque wrench.)  
  - *Coolant System Service:* Drain and refill radiator/engine coolant, bleed air from system. (Tools: drain pan, coolant funnel.)  
  - *Accessory Belt Replacement:* Replace serpentine belt(s). (Tools: wrench for belt tensioner.)  
  - *Transmission Service:* Flush or replace automatic transmission fluid (may require vacuum pump) and filter.  
  - *Suspension/Steering:* Replace shocks/struts, tie-rod ends, or ball joints (requires specialty tools like spring compressors).  
  - *Wheel Alignment:* Adjust camber/toe with alignment machine (often done by specialist shops).

---

## deep-research-report-random-conversation.md:11

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses using scan tool data and test equipment to diagnose specific faults such as engine misfires, sensor failures, and EV battery SoC issues, which is diagnostic in nature.

- *Wheel Alignment:* Adjust camber/toe with alignment machine (often done by specialist shops).  
  - *Advanced Diagnostics:* Use scan tool data and test equipment to diagnose engine misfires, sensor failures, EV battery SoC issues, etc.

---

## deep-research-report-random-conversation.md:12

**Category:** `automotive_diagnostics`  
**Reason:** It describes fault-finding procedures and specialized repair tasks that require diagnostic reasoning and tooling.

- **Advanced Tasks:** Major repairs or specialized EV work, requiring extensive training and equipment:
  - *Engine Overhaul:* Rebuild engine (replace pistons, bearings, head gaskets). (Requires engine crane, full toolset, precision measuring tools.)  
  - *Timing Belt/Chain Replacement:* Align cam and crank timing marks, replace belt/chain and tensioners. (Very precise, engine may need partial disassembly.)  
  - *Clutch/Transmission Rebuild:* Remove and disassemble transmission; replace clutch or internals. (Tools: transmission jack, alignment tool.)  
  - *Hybrid/EV Service:* Handle high-voltage systems (battery pack/module replacement, inverters, electric motor diagnostics). Requires HV-rated PPE, insulated tools, and specialized training.  
  - *ADAS Calibration:* Recalibrate advanced driver-assistance systems (cameras, radar) after repairs, using OEM diagnostic software.  

The competency matrix below summarizes tasks with skill level and tools needed:

---

## deep-research-report-random-conversation.md:13

**Category:** `automotive_fundamentals`  
**Reason:** The markdown lists basic tools for routine maintenance tasks, which are core concepts about vehicle servicing.

| Task                           | Basic (Tools)                              | Intermediate (Tools)                       | Advanced (Tools)                                   |
|--------------------------------|--------------------------------------------|--------------------------------------------|----------------------------------------------------|
| **Oil & Filter Change**        | ✓ Drain pan, wrench, oil filter wrench     |                                            |                                                    |
| **Spark Plug Replacement**     | ✓ Socket set, gap tool                     |                                            |                                                    |
| **Tire Rotation / Pressure**   | ✓ Jack, stands, air gauge                  |                                            |                                                    |

---

## deep-research-report-random-conversation.md:14

**Category:** `automotive_diagnostics`  
**Reason:** The snippet describes OBD-II diagnostics as a task requiring a scan tool, fitting fault-finding and diagnostic workflows.

| **Brake Pad/Shoe Replacement** |                                            | ✓ Jack, lug wrench, brake caliper tools    |                                                    |
| **Coolant Flush/Refill**       |                                            | ✓ Drain pan, coolant funnel                |                                                    |
| **Accessory Belt Replacement** |                                            | ✓ Wrenches (for tensioner pulley)          |                                                    |
| **Wheel Alignment**            |                                            | ✓ Alignment rack/machine                   |                                                    |
| **OBD-II Diagnostics (Scan)**  | ✓ OBD-II scan tool                         |                                            |                                                    |

---

## deep-research-report-random-conversation.md:15

**Category:** `automotive_diagnostics`  
**Reason:** The table lists diagnostic tools and equipment needed for various repair procedures, focusing on fault-finding and tool requirements rather than core concepts or general automotive information.

| **Engine Tuning (software)**   |                                            | ✓ ECU scan tool, multimeter                |                                                    |
| **Timing Belt/Chain Replace**  |                                            |                                            | ✓ Service manual, torque wrench, engine support    |
| **Clutch or Trans. Rebuild**   |                                            |                                            | ✓ Transmission jack, specialty tools               |
| **Hybrid/EV Battery Service**  |                                            |                                            | ✓ High-voltage PPE, insulated tools, diagnostic EV scan tool |
| **ADAS/RADAR Calibration**     |                                            |                                            | ✓ OEM calibration tool, targets/panels             |

---

## deep-research-report-random-conversation.md:16

**Category:** `automotive_diagnostics`  
**Reason:** The flowchart outlines a diagnostic workflow from inspection to repair and verification, focusing on fault-finding and service task identification.

```mermaid
flowchart LR
    A[Vehicle Arrival/Check-In] --> B[Initial Visual Inspection]
    B --> C[Diagnostic Checks (Scan Tool, Multimeter)]
    C --> D[Identify Service Tasks]
    D --> E[Perform Maintenance/Repair]
    E --> F[Quality Check & Road Test]
    F --> G[Update Service Records & Customer Review]

---

## deep-research-report-random-conversation.md:17

**Category:** `automotive_fundamentals`  
**Reason:** Describes safety practices, PPE, and waste handling—core concepts of automotive shop fundamentals.

```

## Safety, Tools, and Diagnostic Equipment  
**Safety:** Automotive work involves hazards (heavy loads, chemicals, electricity). Technicians must follow OSHA guidelines for shop safety: use appropriate **PPE** (eye protection, gloves, hearing protection), lockout/tagout during electrical work, safe lifting practices, proper ventilation, and keep a clean workspace. **Oil, coolant, and other waste fluids** must be collected and disposed of according to EPA regulations. Vehicle lifts and jack stands must be used properly to prevent collapse.

---

## deep-research-report-random-conversation.md:18

**Category:** `other_automotive_information`  
**Reason:** Lists tools and equipment without discussing core concepts or diagnostic fault-finding procedures.

**Essential Tools & Equipment:** 
- **Multimeter:** For testing battery voltage, charging system, and electrical circuits.  
- **OBD-II Scan Tool:** Reads engine/ABS/Airbag/EPS diagnostic trouble codes and live data. Required for most diagnostics on modern vehicles.  
- **Torque Wrench:** Ensures bolts (wheel lug nuts, engine components) are tightened to spec without over- or under-tightening.  
- **Floor Jack & Stands / Lift:** Safely raises vehicle for undercarriage access.  
- **Brake Bleeder Kit:** Vacuum or pressure bleeder for replacing brake fluid.  
- **Compression Tester:** Checks engine cylinder compression.  
- **Fuel Pressure Gauge:** Diagnoses fuel system (fuel pump, regulator).  
- **AC Refrigerant Recovery Machine:** Required for servicing vehicle A/C (EPA Section 609-certified technicians).  
- **Diagnostic Oscilloscope:** For advanced electrical/sensor waveform analysis (advanced shops).

---

## deep-research-report-random-conversation.md:19

**Category:** `automotive_fundamentals`  
**Reason:** It describes essential tools and calibration practices needed for accurate automotive work.

High-end shops may also use frame racks (for collision repair), engine dynos, and thermal cameras. Regular calibration and maintenance of tools is important for accuracy and safety.

## Regulatory, Certification, and Training Standards  
Automotive service technicians must often meet regulatory and certification requirements:

---

## deep-research-report-random-conversation.md:20

**Category:** `automotive_fundamentals`  
**Reason:** It describes industry certifications and training related to automotive knowledge and standards.

- **ASE Certification (Automotive Service Excellence):** Widely recognized industry certification. Tests cover engine repair, brakes, electrical, A/C, etc. ASE certification is valid for **5 years**, after which technicians must take recertification tests. Many employers prefer or require ASE-certified technicians.  
- **Manufacturer Training:** Automakers (e.g. GM, Ford, Toyota) offer factory-specific training programs and certifications for their brands (often required for warranty work). These can range from dealer-only courses to public OEM-certified programs.  
- **EPA Section 609 Certification:** Under the Clean Air Act, any technician working on motor vehicle air conditioners must be trained and certified in refrigerant handling and recovery. Approved training providers include ASE and technical schools.

---

## deep-research-report-random-conversation.md:21

**Category:** `other_automotive_information`  
**Reason:** It discusses regulatory compliance, licensing, and professional development credits, which are not core technical fundamentals or diagnostic procedures.

- **OSHA Compliance:** Automotive shops must comply with OSHA standards (Hazard Communication, PPE, electrical safety, etc.). While there is no specific “auto mechanic license” at the federal level, shops should train employees on general industry safety. (Some states may have additional licensing for emissions testing or brake work.)  
- **State/Local Emission Programs:** Some states (e.g. California) require technicians or shops to be licensed for smog inspections. These programs have their own training and certification rules.  
- **Professional Development Credits:** Associations like ASA (Automotive Service Assoc.) and AMi (Auto Management Institute) offer continuing education credits and designations (e.g. Accredited Automotive Manager) for management and technical learning.

---

## deep-research-report-random-conversation.md:22

**Category:** `other_automotive_information`  
**Reason:** It describes CE course topics and objectives, which is informational but not core fundamentals or diagnostic procedures.

## Sample Continuing-Education Course Topics  
Continuing-education (CE) courses for automotive technicians typically focus on new technologies and skills. Sample topics with objectives and assessment methods might include:

---

## deep-research-report-random-conversation.md:23

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic labs and fault-finding tasks using scan tools and oscilloscopes.

- **Hybrid/EV Systems:** *Learning Objectives:* Identify hybrid components (battery, inverter, motors) and understand safe procedures. *Assessment:* Hands-on lab replacing a hybrid battery module and a written quiz on HV safety.  
- **Advanced Diagnostics (Electronics):** *Objectives:* Use oscilloscope and scan tool to diagnose complex electrical/sensor faults. *Assessment:* Diagnostic lab where student finds and fixes a no-start condition.  
- **Engine Performance Tuning:** *Objectives:* Calibrate ignition timing and fuel systems for maximum efficiency. *Assessment:* Demonstration of adjusting timing and measuring improved performance on dyno.  
- **Brake Systems & ABS/ESC:** *Objectives:* Understand hydraulic brake service and ABS maintenance. *Assessment:* Replace brake pads, bleed system, then use scan tool to test ABS fault codes.

---

## deep-research-report-random-conversation.md:24

**Category:** `other_automotive_information`  
**Reason:** The content describes training objectives and assessments related to HVAC safety and customer service communication, which are peripheral to core automotive fundamentals or diagnostic processes.

- **HVAC Refrigerant Safety:** *Objectives:* Learn refrigerant recovery and leak testing per EPA requirements. *Assessment:* Certificate upon passing EPA 609 exam and demonstrated use of A/C recovery machine.  
- **Customer Service & Communication:** *Objectives:* Develop skills to explain repairs and maintenance to customers. *Assessment:* Role-play scenarios and graded written service write-ups.

---

## deep-research-report-random-conversation.md:25

**Category:** `automotive_fundamentals`  
**Reason:** It explains core concepts like service intervals, maintenance schedules, and warranty requirements.

Courses are often a mix of lectures, hands-on labs, and testing (written exams or practical demonstrations). ASE and community colleges frequently offer such modules.

## Recordkeeping, Service Intervals, and Customer Communication  
Maintaining accurate service records is crucial. Technicians should log all work performed (parts, labor, mileage, date) in a digital system or service booklet. These records prove compliance with **warranty** maintenance requirements and help diagnose future issues. Owners should follow the **maintenance schedule** in the owner’s manual (stick to OEM-recommended intervals). For example, many cars require oil changes every 5,000–7,500 miles (or longer with synthetic oil) and spark plug changes around 60,000–100,000 miles. For EVs, maintenance needs are different (no oil changes or spark plugs), but tire rotations, brake fluid, and cabin air filter changes remain.

---

## deep-research-report-random-conversation.md:26

**Category:** `other_automotive_information`  
**Reason:** It discusses customer communication and service practices, which are not core technical fundamentals or diagnostic procedures.

Effective **customer communication** is key. Technicians should explain findings in simple terms, show any worn parts (e.g. brake pad thickness), and justify recommended services. Written estimates and printed manufacturer maintenance schedules help customers understand necessary work. Transparency builds trust: avoid unnecessary upsells by referring strictly to the vehicle’s schedule or observed failures. Reminder systems (email/text) for upcoming services also improve customer retention.

**Sources:** Information above is drawn from OEM manuals and industry authorities (e.g. ASE and EPA certification rules), automotive reference guides, and reputable trade resources (Carfax maintenance guide, SAE literature).

---

## fault_profiles.md:0

**Category:** `automotive_diagnostics`  
**Reason:** The text explains how faults manifest on OBD and how to simulate them, focusing on diagnostic reasoning and symptom-to-cause workflows.

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

---

## fault_profiles.md:1

**Category:** `automotive_diagnostics`  
**Reason:** The text explains how to simulate faults by overriding PIDs and using diagnostic steps, which falls under fault finding and diagnostic workflows.

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

---

## fault_profiles.md:2

**Category:** `automotive_diagnostics`  
**Reason:** It explains fault-finding workflows, session requirements, and diagnostic steps for applying fault profiles.

**Important limitations**

- Overrides are **static** — one set of values per session. Load-dependent faults (weak fuel pump, fan failure) need **separate sessions** (e.g. idle vs cruise).
- Time-varying faults (rising coolant, drifting trims) need **multiple sessions** or manual value changes mid-recording.
- Random variation (misfire, unstable RPM) is simulated by returning a value from a range on each poll.

**PID names** match python-OBD command names: `RPM`, `SPEED`, `COOLANT_TEMP`, `SHORT_FUEL_TRIM_1`, `LONG_FUEL_TRIM_1`, `MAF`, `INTAKE_PRESSURE`, `INTAKE_TEMP`, `ENGINE_LOAD`, `THROTTLE_POS`, `O2_B1S2`, `CONTROL_MODULE_VOLTAGE`, etc. See [emulator_car_queries.md](emulator_car_queries.md) for healthy baselines.

---

## Recording training sessions

After applying a fault profile:

---

## fault_profiles.md:3

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault labeling, DTC ground truth, and diagnostic workflow for training sessions.

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

---

## fault_profiles.md:4

**Category:** `automotive_diagnostics`  
**Reason:** Describes a specific fault and its diagnostic implications.

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

---

## fault_profiles.md:5

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault-finding for a vacuum leak with symptom patterns, OBD signatures, and detection hints.

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

---

## fault_profiles.md:6

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, symptom-to-cause reasoning, and diagnostic steps for MAF sensor issues.

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

---

## fault_profiles.md:7

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault detection and diagnostic patterns for stuck open EGR, including OBD signatures and simulation guidance.

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

---

## fault_profiles.md:8

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, symptom patterns, and diagnostic simulation steps for a specific issue.

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

---

## fault_profiles.md:9

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, symptom patterns, and typical DTCs for diagnosing injector and ignition issues.

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

---

## fault_profiles.md:10

**Category:** `automotive_diagnostics`  
**Reason:** Describes a fault (thermostat stuck open) and its OBD signature and diagnostic interpretation.

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

---

## fault_profiles.md:11

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, DTC meanings, and diagnostic steps for thermostat failures.

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

---

## fault_profiles.md:12

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures and diagnostic steps for cooling fan failure and water pump degradation.

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

---

## fault_profiles.md:13

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, symptom-to-cause reasoning, and diagnostic simulation steps.

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

---

## fault_profiles.md:14

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures and diagnostic steps for specific DTCs.

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

---

## fault_profiles.md:15

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault simulation and DTC interpretation for O2 sensor issues.

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

---

## fault_profiles.md:16

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, DTC meanings, and diagnostic steps for sensor failures.

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

---

## fault_profiles.md:17

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, symptom patterns, and diagnostic steps for sensor failures.

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

---

## fault_profiles.md:18

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures and diagnostic patterns for voltage issues.

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

---

## fault_profiles.md:19

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, symptom patterns, and diagnostic simulation steps for specific DTCs and engine issues.

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

---

## fault_profiles.md:20

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault signatures, DTC associations, and diagnostic simulation steps.

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

---

## fault_profiles.md:21

**Category:** `automotive_diagnostics`  
**Reason:** The text describes fault symptoms, simulation guidance, and DTC pairing for diagnosing transmission and drivetrain issues.

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

---

## fault_profiles.md:22

**Category:** `automotive_diagnostics`  
**Reason:** The chunk describes fault mapping to detector layers, DTC override options, and diagnostic workflows, which aligns with fault finding and diagnostic processes.

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

---

## pid_definitions.md:0

**Category:** `automotive_fundamentals`  
**Reason:** Defines what a PID is, its role in OBD-II, and provides core concepts like modes and example requests.

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

---

## pid_definitions.md:1

**Category:** `automotive_fundamentals`  
**Reason:** Describes Mode 01 request/response format and PID 0x0C encoding for RPM, a core OBD-II concept.

In **Mode 01**, the scan tool sends `01 XX` where `XX` is the PID hex code. The ECU replies with `41 XX` plus encoded bytes. python-OBD wraps this as named commands (`obd.commands.RPM`, etc.).

```text
Request:  01 0C          (Mode 01, PID 0x0C = RPM)
Response: 41 0C 14 50    (RPM = 0x1450 / 4 = 1300 rpm)

---

## pid_definitions.md:2

**Category:** `automotive_fundamentals`  
**Reason:** Describes core PIDs and naming conventions for OBD-II parameters, which are fundamental concepts in automotive diagnostics.

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

---

## pid_definitions.md:3

**Category:** `automotive_fundamentals`  
**Reason:** The text defines specific OBD-II PIDs, their hex codes, units, and basic meanings, which are core concepts of automotive fundamentals.

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

---

## pid_definitions.md:4

**Category:** `automotive_fundamentals`  
**Reason:** The excerpt defines PIDs, their hex codes, units, and describes what each sensor measures, which are core concepts of OBD-II fundamentals.

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

---

## pid_definitions.md:5

**Category:** `automotive_fundamentals`  
**Reason:** The text explains core OBD-II PIDs, fuel trim concepts, and their meanings, which are fundamental automotive diagnostic concepts.

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

---

## pid_definitions.md:6

**Category:** `automotive_fundamentals`  
**Reason:** It explains PID encoding, typical ranges, and how sensor values are derived, which are core concepts.

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

---

## pid_definitions.md:7

**Category:** `automotive_diagnostics`  
**Reason:** It explains how to interpret coolant temperature PID behavior for fault diagnosis.

**Encoding:** `byte = °C + 40` (so −40°C → `0x00`, 90°C → `0x82`).

**Diagnostic use:** Coolant stuck low after long `RUN_TIME` → thermostat stuck open. Rapid rise → stuck closed or low coolant. High coolant only at idle/low speed → fan failure.

---

### Oxygen sensors and emissions

---

## pid_definitions.md:8

**Category:** `automotive_fundamentals`  
**Reason:** The text defines specific PIDs, their hex codes, units, and describes what each sensor measures, which are core concepts in automotive fundamentals.

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

---

## pid_definitions.md:9

**Category:** `automotive_fundamentals`  
**Reason:** Describes O2 sensor behavior, P0420 fault, and voltage PIDs with units and typical ranges, which are core concepts.

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

---

## pid_definitions.md:10

**Category:** `automotive_diagnostics`  
**Reason:** The text describes diagnostic commands and DTC handling, which falls under fault finding and diagnostic procedures.

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

---

## pid_definitions.md:11

**Category:** `automotive_fundamentals`  
**Reason:** Describes freeze frame concept and encoding for building emulator overrides, which are core OBD-II concepts.

**Freeze frame (`DTC_*` commands):** Snapshot of key PIDs at the moment a DTC was stored. Useful for validating that live fault simulation matches stored evidence.

---

## Encoding quick reference

Formulas for building emulator overrides (full list in [fault_simulation.md](fault_simulation.md)).

---

## pid_definitions.md:12

**Category:** `automotive_fundamentals`  
**Reason:** The text defines specific OBD-II PIDs, their encoding/decoding formulas, and raw probe usage, which are core concepts of automotive fundamentals.

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

---

## pid_definitions.md:13

**Category:** `automotive_fundamentals`  
**Reason:** The text defines and lists key PIDs for various subsystems, explaining their purpose and associated faults, which aligns with core concepts of PIDs, encoding, and OBD-II fundamentals.

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

---

## pid_definitions.md:14

**Category:** `automotive_fundamentals`  
**Reason:** The file defines PIDs and explains their structure and meaning.

Details per fault: [fault_profiles.md](fault_profiles.md).

---

## See also

- [toyota_pid_definitions.md](toyota_pid_definitions.md) — Toyota hybrid extended PIDs and ECU headers
- [toyota_dtc_definitions.md](toyota_dtc_definitions.md) — Toyota and hybrid DTC reference
- [../README.md](../README.md) — pipeline architecture and streaming PIDs list
- [test_commands.md](test_commands.md) — connect and query from Python

---

## toyota_dtc_definitions.md:0

**Category:** `automotive_fundamentals`  
**Reason:** Explains DTC structure, storage, and OBD-II modes (03, 07, 04, 02) used for retrieving and clearing codes.

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

---

## toyota_dtc_definitions.md:1

**Category:** `automotive_fundamentals`  
**Reason:** Explains DTC structure and MIL behavior, which are core concepts.

**MIL (check engine light):** Illuminates for most `P` codes that affect emissions. Some hybrid codes also trigger the **master warning** or **hybrid system** indicator on the dash — not always the same as MIL.

**Emulator note:** The `car` scenario returns **`GET_DTC: []`** by default. See [fault_simulation.md](fault_simulation.md) for optional DTC simulation.

---

## DTC format

```text
  P 0  1  7  1
  │ │  └──┴──┴─ SAE fault number (0–9999)
  │ └────────── Second digit: system category
  └──────────── First letter: domain

---

## toyota_dtc_definitions.md:2

**Category:** `automotive_fundamentals`  
**Reason:** Explains OBD-II P-code categories, hybrid-specific codes, and status nibbles in Mode 03/07.

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

---

## toyota_dtc_definitions.md:3

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses DTC status nibbles, fault detection states, and how to treat confirmed DTCs as ground truth for training labels, which pertains to fault diagnosis and interpretation.

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

---

## toyota_dtc_definitions.md:4

**Category:** `automotive_diagnostics`  
**Reason:** The text lists DTC codes with descriptions and typical fault profiles, which is diagnostic information.

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

---

## toyota_dtc_definitions.md:5

**Category:** `automotive_diagnostics`  
**Reason:** The text explains misfire DTCs and their typical fault profiles, which is diagnostic information.

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

---

## toyota_dtc_definitions.md:6

**Category:** `automotive_diagnostics`  
**Reason:** The text lists DTC codes with descriptions and typical fault profiles, which is diagnostic information.

### Cooling

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0128** | Coolant Thermostat (coolant temp below regulating temp) | Thermostat stuck open |
| **P0217** | Engine Coolant Over Temperature | Thermostat stuck closed, fan failure, low coolant, head gasket |
| **P0117** | ECT Sensor Circuit Low | Coolant temp sensor failure (implausible cold) |
| **P0118** | ECT Sensor Circuit High | Coolant temp sensor short/high |

### Emissions / O2 / catalyst

---

## toyota_dtc_definitions.md:7

**Category:** `automotive_diagnostics`  
**Reason:** The text lists DTC codes with descriptions and typical fault profiles, which is diagnostic information.

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

---

## toyota_dtc_definitions.md:8

**Category:** `automotive_diagnostics`  
**Reason:** The text lists specific DTC codes (P0562, P0563) and their fault profiles, which is diagnostic information.

### Electrical

| Code | Description | Typical fault profile |
|------|-------------|----------------------|
| **P0562** | System Voltage Low | Alternator failure, weak battery |
| **P0563** | System Voltage High | Voltage regulator failure |

---

## Toyota hybrid DTCs (P0Axx and related)

Generic SAE hybrid codes used heavily on Toyota THS (Prius, Auris Hybrid, Corolla Hybrid, etc.).

### HV battery

---

## toyota_dtc_definitions.md:9

**Category:** `automotive_diagnostics`  
**Reason:** The text lists DTC codes with descriptions and typical causes, which is diagnostic fault-finding information.

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

---

## toyota_dtc_definitions.md:10

**Category:** `automotive_diagnostics`  
**Reason:** The text lists DTC codes with descriptions and typical causes, which is diagnostic information.

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

---

## toyota_dtc_definitions.md:11

**Category:** `automotive_diagnostics`  
**Reason:** The text describes specific DTC codes, their descriptions, and diagnostic notes for troubleshooting hybrid system issues.

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

---

## toyota_dtc_definitions.md:12

**Category:** `automotive_diagnostics`  
**Reason:** The text explains how DTCs are stored and used in freeze frame data for diagnostic interpretation.

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

---

## toyota_dtc_definitions.md:13

**Category:** `automotive_diagnostics`  
**Reason:** The snippet shows Python code to query and retrieve stored and pending DTCs, which is a diagnostic activity.

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

---

## toyota_dtc_definitions.md:14

**Category:** `automotive_diagnostics`  
**Reason:** It shows a Python snippet for clearing DTCs, which is a diagnostic action.

```

Clear after testing:

```python
c.query(obd.commands.CLEAR_DTC)

---

## toyota_dtc_definitions.md:15

**Category:** `automotive_diagnostics`  
**Reason:** The text explains how DTCs are mapped to pipeline layers, diagnostic rules, and labeling strategies, focusing on fault detection and interpretation.

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

---

## toyota_dtc_definitions.md:16

**Category:** `automotive_fundamentals`  
**Reason:** The text lists external references for DTC standards and Toyota documentation, which are core concepts in automotive fundamentals.

### External references

- [SAE J2012](https://www.sae.org) — standard DTC definitions (P0/P2)
- Toyota service manual / Techstream — authoritative P1/P3 and infocodes
- [PriusChat DTC forums](https://priuschat.com) — community hybrid code experience

---

## toyota_pid_definitions.md:0

**Category:** `automotive_fundamentals`  
**Reason:** It explains OBD modes, PID layers, and how Toyota extended PIDs are accessed, which are core concepts.

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

---

## toyota_pid_definitions.md:1

**Category:** `automotive_fundamentals`  
**Reason:** Describes generic PID sources, CAN headers, Mode 21/22 usage, and decode formulas—core concepts of OBD-II operation.

Generic PIDs (`RPM`, `COOLANT_TEMP`, fuel trims, etc.) come from the **engine ECU** at CAN header **`7E0`**. Hybrid battery, motor, and inverter data live on **other ECUs** and require:

1. The correct **CAN receive address** (header), e.g. `7E3` for HV battery
2. Toyota **Mode 21 or 22** request with a **manufacturer PID**
3. A **decode formula** on response bytes A, B, C…

Newer Toyota hybrids (2016+) often use **Mode 22** (2-byte PID) instead of Mode 21. Always verify on your model year — a PID that works on Gen2 Prius may fail on Gen4 with response `7F 11` (mode not supported).

---

## Toyota ECU addresses (common)

---

## toyota_pid_definitions.md:2

**Category:** `automotive_fundamentals`  
**Reason:** Describes ECU addresses, request/response IDs, and standard Mode 01 PIDs, which are core OBD-II concepts.

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

---

## toyota_pid_definitions.md:3

**Category:** `automotive_fundamentals`  
**Reason:** Describes core OBD-II Mode 01 PIDs, their units, and meaning for Toyota hybrid engines.

### Engine / emissions (same as generic)

Toyota Atkinson-cycle engines expose normal Mode 01 PIDs on `7E0`: `RPM`, `SPEED`, `MAF`, `INTAKE_PRESSURE`, `SHORT_FUEL_TRIM_1`, `LONG_FUEL_TRIM_1`, `COOLANT_TEMP`, `O2_B1S2`, `O2_S1_WR_*`, catalyst temps, etc.

Fuel trim interpretation is identical to [pid_definitions.md](pid_definitions.md). Toyota tends toward **long warm-up** and **conservative trim limits** before setting lean/rich codes.

### Toyota-specific Mode 01 entries

| PID (hex) | python-OBD | Unit | Meaning |
|-----------|------------|------|---------|
| `0x5B` | `HYBRID_BATTERY_REMAINING` | % | Hybrid/EV battery **state of health / remaining life** estimate (when ECU supports it; often `NULL` on emulator) |
| `0x51` | `FUEL_TYPE` | enum | Often reports **Gasoline** on Auris Hybrid (ICE + HV system) |

### Readiness and compliance

---

## toyota_pid_definitions.md:4

**Category:** `automotive_fundamentals`  
**Reason:** Describes OBD-II readiness monitors, compliance commands, and extended hybrid system PIDs, which are core concepts of automotive fundamentals.

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

---

## toyota_pid_definitions.md:5

**Category:** `automotive_fundamentals`  
**Reason:** The text defines PIDs, their encoding formats, units, and typical ranges, which are core concepts of automotive fundamentals.

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

---

## toyota_pid_definitions.md:6

**Category:** `automotive_fundamentals`  
**Reason:** The snippet defines PIDs, their codes, units, and meanings, which are core concepts in automotive fundamentals.

| HV discharge power limit | `21CF` | `F − 64` | kW | Max discharge to motors |
| HV battery fan mode | `21CF` | `I` | enum | Forced cooling status |

---

## toyota_pid_definitions.md:7

**Category:** `automotive_diagnostics`  
**Reason:** The text explains diagnostic interpretation of battery health via voltage spread and describes specific OBD-II mode 21 PIDs for hybrid control ECU, focusing on fault analysis and system behavior.

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

---

## toyota_pid_definitions.md:8

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses fault-finding and diagnostic interpretation of hybrid battery and temperature signals in Toyota hybrids.

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

---

## toyota_pid_definitions.md:9

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses fault simulation, mislabeling normal hybrid behavior as faults, and guidance on interpreting OBD signals during diagnostics.

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

---

## toyota_pid_definitions.md:10

**Category:** `automotive_fundamentals`  
**Reason:** Describes core OBD-II PID concepts, emulator availability, and manufacturer-specific extensions.

| Toyota-relevant command | Emulator sample | Extended? |
|-------------------------|-----------------|-----------|
| `HYBRID_BATTERY_REMAINING` | NULL | Mode 01 placeholder |
| `RPM`, `SPEED`, `MAF`, trims, coolant, O2 | ✅ live values | No |
| HV SOC, block voltages, MG temps | ❌ not available | Needs Mode 21/22 + header |
| Transmission temps | ❌ not in 86-command list | Manufacturer PIDs |

For pipeline v1, train on **ICE-side PIDs** from the emulator. Plan Mode 22 integration separately for HV battery health on real cars.

---

## Accessing Toyota PIDs in software

---

## toyota_pid_definitions.md:11

**Category:** `automotive_diagnostics`  
**Reason:** Describes fault-finding steps and raw request shapes for accessing Toyota PIDs.

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

---

## toyota_pid_definitions.md:12

**Category:** `automotive_diagnostics`  
**Reason:** The text discusses DTC definitions and diagnostic guidance for HV battery health.

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

---

## toyota_pid_definitions.md:13

**Category:** `automotive_diagnostics`  
**Reason:** The chunk discusses DTC definitions and fault finding, which falls under automotive diagnostics.

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

---

## toyota_pid_definitions.md:14

**Category:** `automotive_fundamentals`  
**Reason:** The text lists external references that describe PID definitions, encoding, and OBD-II modes for Toyota hybrid vehicles, which are core concepts in automotive fundamentals.

### External references

- [Torque PIDs for Toyota Auris Hybrid (2017)](http://zansprojects.blogspot.com/2018/12/torque-pids-for-toyota-auris-hybrid.html) — Auris-validated CSV
- [PriusChat custom PID threads](https://priuschat.com) — community Mode 21/22 formulas
- [Prius Gen2 CAN/OBD2 PID compilation (PDF)](https://attachments.priuschat.com/attachment-files/2021/09/211662_Prius22009_CAnCodes.pdf) — header and byte layouts

---
