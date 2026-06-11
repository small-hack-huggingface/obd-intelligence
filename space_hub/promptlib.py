"""Prompt formatting shared with training (mirrors distill.py exactly)."""
import numpy as np

CHANNELS = ["rpm", "speed_kph", "coolant_temp_c", "engine_load_pct", "throttle_pct",
            "intake_temp_c", "maf_gps", "map_kpa", "stft_pct", "ltft_pct", "o2_b1s2_v",
            "control_module_voltage_v", "timing_advance_deg", "catalyst_temp_c",
            "commanded_egr_pct", "evap_purge_pct"]

STUDENT_SYSTEM = (
    "You are Pocket Mechanic, a trusted mechanic in the driver's pocket. You read "
    "OBD-II sensor data and explain car problems in plain English. Always answer in "
    "this structure: 1. WHAT'S HAPPENING  2. ROOT CAUSE  3. WHAT TO DO (cheapest "
    "fix first, with cost and time)  4. WATCH OUT FOR (mechanic upsell traps). Be "
    "honest, specific, and protect the driver's wallet."
)


FAULT_REFERENCE = {
    "vacuum_leak": "fix: find leak (spray test $5 / smoke test $60-120), hose $5-20 DIY, intake gasket $150-350 shop. Trap: 'new intake manifold' or $200-400 'fuel system service'.",
    "dirty_maf": "fix: MAF cleaner spray $10, 15 min DIY; sensor $80-250 only if cleaning fails. Trap: instant $350+ sensor replacement or 'throttle body service' bundle.",
    "air_filter_restriction": "fix: air filter $15-30, 5 min DIY, no tools. Trap: $50-90 labor for the swap; 'induction cleaning service'.",
    "egr_stuck_open": "fix: clean EGR valve $10 + 1-2h DIY; replacement $150-400. Trap: $400+ 'full decarbonization service'.",
    "fuel_pump_weak": "fix: fuel pressure gauge test $0-50 confirms; pump assembly $150-350 part + 1-3h labor. Trap: injectors or 'fuel system flush' first — load-only trims point at pressure.",
    "injector_leak_rich": "fix: injector leak-down test; single injector $60-150 + 1h. Trap: 'replace all injectors as a set'.",
    "ignition_misfire": "FLASHING CEL = stop driving (cooks the $1000+ cat). fix: swap coil to confirm ($0), plug $5-25 DIY 30min, coil $40-100 DIY 20min. Trap: $300-600 'tune-up package'.",
    "spark_plug_wear": "fix: full plug set $20-80, 1h DIY. Trap: plugs+coils+wires 'while we're in there'.",
    "thermostat_stuck_open": "fix: thermostat $15-40 part, 1-2h DIY or $150-250 shop. Trap: radiator/head-gasket quotes — low steady temp is the opposite signature.",
    "overheating": "STOP DRIVING — warped head is $1500-3000. fix: thermostat $150-250 or water pump $300-600. Trap: engine replacement quotes without a compression test.",
    "cooling_fan_failure": "fix: check fan fuse/relay $5-15 DIY first; fan motor $80-200 + 1h. Trap: $600+ 'radiator + fan assembly' for a $10 relay.",
    "low_coolant": "fix: top up $15, pressure test $30-60 to find leak; hose $20-50. Trap: stop-leak additives; head-gasket scares without a combustion-gas test.",
    "catalyst_degradation": "fix FIRST rule out: exhaust leak check $0-30, O2 sensor $50-150. Real cat: aftermarket CARB-compliant $300-900 (OEM $1000-2500 NOT required by law in most states). Trap: instant OEM cat quote.",
    "catalyst_restriction": "fix: backpressure test $50-100 confirms; then cat as above. Trap: tune-up parts chasing an exhaust restriction.",
    "evap_purge_stuck": "fix: purge valve $20-60, 20-30min DIY (two clips + a hose). Trap: $500 'EVAP system + canister' bundle for a $30 valve.",
    "o2_sensor_drift": "fix: upstream O2 sensor $50-150, 30min DIY with $10 socket. Trap: replacing all sensors 'as a set'.",
    "o2_sensor_stuck": "flat-lined sensor (live ones always oscillate). fix: sensor $50-150, 30min DIY. Trap: 'fuel system cleaning' for a dead sensor.",
    "alternator_failure": "will strand you soon. fix: free battery/alternator test at parts stores; belt first $20-60; alternator $150-400 + 1-2h. Trap: 'new battery' alone — it dies again in days.",
    "voltage_regulator_high": "15V+ cooks battery and electronics, urgent-ish. fix: alternator (regulator internal) $150-400. Trap: chasing blown bulbs without fixing source voltage.",
    "map_sensor_fault": "fix: check connector/vacuum line $0; sensor $40-120, 15min DIY. Trap: $300+ 'drivability diagnostic package'.",
    "tps_sensor_stuck": "fix: connector check $0; TPS $30-100 30min where serviceable; drive-by-wire throttle body $200-500 only after live-data confirmation. Trap: full throttle body on a $40 TPS car.",
    "healthy": "nothing owed. Traps shops sell healthy cars: induction cleaning, flushes 'by mileage', wallet-flush maintenance packages.",
    "no_fault": "nothing owed. Traps shops sell healthy cars: induction cleaning, flushes 'by mileage', wallet-flush maintenance packages.",
}


def reference_card(fault_names):
    lines = [f"- {f}: {FAULT_REFERENCE[f]}" for f in fault_names if f in FAULT_REFERENCE]
    return "MECHANIC'S REFERENCE CARD (typical 4-cyl sedan economics):\n" + "\n".join(lines)


def window_stats(w):
    lines = ["PID                       mean      std    slope/min      min      max"]
    dur_min = max(len(w) / 60.0, 1e-6)
    for c in CHANNELS:
        v = w[c].to_numpy()
        slope = (v[-1] - v[0]) / dur_min
        lines.append(f"{c:<24}{v.mean():>9.2f}{v.std():>9.2f}{slope:>12.2f}{v.min():>9.2f}{v.max():>9.2f}")
    return "\n".join(lines)


def last30(w):
    tail = w.tail(30)
    return ", ".join(f"{c}={tail[c].mean():.2f}" for c in CHANNELS)


def build_inference_prompt(window, vehicle, preds, dtc, question, context,
                           include_reference=True):
    top = list(preds.items())[:3]
    pred_txt = ", ".join(f"{n}: {p:.0%}" for n, p in top)
    ref = (reference_card([n for n, _ in top]) + "\n\n") if include_reference else ""
    return f"""VEHICLE: {vehicle}
DRIVE WINDOW: last {len(window) / 60:.1f} min, context: {context}

SENSOR SUMMARY (full window):
{window_stats(window)}

LAST 30 SECONDS (averages): {last30(window)}

ACTIVE DTCs: {dtc or 'none'}
PREDICTOR OUTPUT: {pred_txt}

{ref}DRIVER ASKS: {question}"""
