"""Distill diagnostic explanations from Claude Opus 4.7 into training pairs.

Reads data/synthetic/synthetic_sessions.csv, builds (sensor window + simulated
predictor output + driver question) prompts, and asks the teacher model for a
mechanic-voice explanation. Output is chat-format JSONL ready for LoRA
fine-tuning of the on-device explainer.

Requires ANTHROPIC_API_KEY (env var, or a KEY=VALUE line in ./.env).

    python distill.py --dry-run            # print one assembled prompt, no API calls
    python distill.py --limit 20           # smoke test
    python distill.py                      # full run (resumable; appends to --out)
"""
import argparse
import json
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

MODEL = "claude-opus-4-7"
IN_PRICE, OUT_PRICE = 5.0, 25.0  # $/Mtok
CACHE_WRITE_MULT, CACHE_READ_MULT = 1.25, 0.10

CHANNELS = ["rpm", "speed_kph", "coolant_temp_c", "engine_load_pct", "throttle_pct",
            "intake_temp_c", "maf_gps", "map_kpa", "stft_pct", "ltft_pct", "o2_b1s2_v",
            "control_module_voltage_v", "timing_advance_deg", "catalyst_temp_c",
            "commanded_egr_pct", "evap_purge_pct"]

VEHICLES = [
    ("2014 Toyota Camry", "2.5L I4", (90_000, 160_000)),
    ("2018 Honda Civic", "1.5L turbo I4", (40_000, 110_000)),
    ("2012 Ford F-150", "5.0L V8", (110_000, 210_000)),
    ("2016 Hyundai Elantra", "2.0L I4", (60_000, 140_000)),
    ("2010 Honda CR-V", "2.4L I4", (130_000, 220_000)),
    ("2019 Mazda 3", "2.5L I4", (30_000, 90_000)),
    ("2008 Toyota Corolla", "1.8L I4", (150_000, 260_000)),
    ("2017 Chevrolet Malibu", "1.5L turbo I4", (50_000, 130_000)),
]

GENERIC_QUESTIONS = [
    "What's wrong with my car?",
    "Is it safe to keep driving?",
    "The check engine light just came on. What should I do?",
    "My mechanic wants $400 to 'look into it'. What is actually going on?",
    "Can I fix this myself or do I need a shop?",
    "How urgent is this?",
]

SYMPTOM_QUESTIONS = {
    "vacuum_leak": ["The idle feels rough and a bit high lately.", "I hear a faint hissing from the engine bay at idle."],
    "dirty_maf": ["The car hesitates when I accelerate.", "Fuel economy has dropped noticeably this month."],
    "air_filter_restriction": ["The car feels sluggish, like it lost power.", "I have to press the gas harder than usual."],
    "egr_stuck_open": ["The engine idles really rough, almost stalls at lights."],
    "fuel_pump_weak": ["It loses power going uphill or when I floor it.", "Sometimes it sputters under hard acceleration."],
    "injector_leak_rich": ["I smell fuel sometimes, and the exhaust smells strong.", "My gas mileage suddenly got much worse."],
    "ignition_misfire": ["The engine shakes at idle and the light is flashing.", "It stumbles and shudders, especially at stoplights."],
    "spark_plug_wear": ["It's been getting slowly worse to start and idle smooth."],
    "thermostat_stuck_open": ["The heater barely gets warm and the temp gauge stays low.", "Engine never seems to warm up fully."],
    "overheating": ["The temperature gauge is climbing into the red!", "Steam is starting to come from under the hood."],
    "cooling_fan_failure": ["It runs hot in traffic but fine on the highway."],
    "low_coolant": ["The temp gauge bounces around weirdly."],
    "catalyst_degradation": ["It smells like rotten eggs and the light came on.", "Failed my emissions test, what now?"],
    "catalyst_restriction": ["The car feels choked, no power at higher speeds."],
    "evap_purge_stuck": ["It idles rough right after I fill up the tank."],
    "o2_sensor_drift": ["Gas mileage has slowly gotten worse over months."],
    "o2_sensor_stuck": ["The check engine light came on but the car feels fine."],
    "alternator_failure": ["My dash lights dim at idle and the battery light flickered.", "The battery keeps dying even though it's new."],
    "voltage_regulator_high": ["Headlights seem super bright and a bulb just blew."],
    "map_sensor_fault": ["It runs terribly, surging and stumbling at all speeds."],
    "tps_sensor_stuck": ["The revs do their own thing, throttle feels disconnected."],
    "healthy": ["Just did a long drive, can you check everything is okay?", "Pre-purchase check: anything wrong with this car?"],
}

CONFUSABLES = {
    "vacuum_leak": ["dirty_maf", "evap_purge_stuck"],
    "dirty_maf": ["vacuum_leak", "air_filter_restriction"],
    "air_filter_restriction": ["dirty_maf", "catalyst_restriction"],
    "egr_stuck_open": ["vacuum_leak", "ignition_misfire"],
    "fuel_pump_weak": ["dirty_maf", "catalyst_restriction"],
    "injector_leak_rich": ["o2_sensor_stuck", "evap_purge_stuck"],
    "ignition_misfire": ["spark_plug_wear", "egr_stuck_open"],
    "spark_plug_wear": ["ignition_misfire", "o2_sensor_drift"],
    "thermostat_stuck_open": ["low_coolant", "cooling_fan_failure"],
    "overheating": ["cooling_fan_failure", "low_coolant"],
    "cooling_fan_failure": ["overheating", "low_coolant"],
    "low_coolant": ["thermostat_stuck_open", "overheating"],
    "catalyst_degradation": ["o2_sensor_drift", "o2_sensor_stuck"],
    "catalyst_restriction": ["air_filter_restriction", "fuel_pump_weak"],
    "evap_purge_stuck": ["vacuum_leak", "injector_leak_rich"],
    "o2_sensor_drift": ["catalyst_degradation", "spark_plug_wear"],
    "o2_sensor_stuck": ["catalyst_degradation", "o2_sensor_drift"],
    "alternator_failure": ["voltage_regulator_high"],
    "voltage_regulator_high": ["alternator_failure"],
    "map_sensor_fault": ["vacuum_leak", "tps_sensor_stuck"],
    "tps_sensor_stuck": ["map_sensor_fault"],
    "healthy": ["o2_sensor_drift", "spark_plug_wear"],
}

# Short system prompt the on-device student model will run with at inference.
STUDENT_SYSTEM = (
    "You are Pocket Mechanic, a trusted mechanic in the driver's pocket. You read "
    "OBD-II sensor data and explain car problems in plain English. Always answer in "
    "this structure: 1. WHAT'S HAPPENING  2. ROOT CAUSE  3. WHAT TO DO (cheapest "
    "fix first, with cost and time)  4. WATCH OUT FOR (mechanic upsell traps). Be "
    "honest, specific, and protect the driver's wallet."
)

# Large frozen teacher system prompt — kept stable for prompt caching.
TEACHER_SYSTEM = """You are Pocket Mechanic, a master automotive technician with 25 years of experience, writing for a driver with zero mechanical knowledge. You read OBD-II sensor data and a fault predictor's output, then explain what is happening in plain English. Your defining trait: you cannot be gaslit and you protect the driver's wallet. You know exactly which repairs are real, what they should cost, and which upsells shops use for each fault.

VOICE RULES
- Plain English. Never use jargon without a one-phrase translation (e.g. "fuel trim — how much extra fuel the computer is adding to compensate").
- Ground every claim in the actual sensor evidence given. Quote the numbers.
- Cheapest plausible fix first. DIY option whenever realistic, with parts cost and time.
- Be honest about uncertainty. If the predictor's top fault is below ~60% or the evidence is mixed, say what would confirm the diagnosis (a $20 smoke test, swapping coils, etc).
- Urgency must be calibrated: overheating and a flashing CEL are stop-driving-now; an EVAP code is "fix it this month".
- Answer the driver's actual question first if they asked one.

OUTPUT FORMAT (always exactly these four numbered sections)
1. WHAT'S HAPPENING — one or two sentences, plain English, referencing the key sensor evidence.
2. ROOT CAUSE — the most likely physical cause, plus the runner-up if confidence is moderate.
3. WHAT TO DO — ordered list, cheapest first. Each step: action, parts cost, labor/time, DIY-able or not.
4. WATCH OUT FOR — the specific upsells and misdiagnoses shops commonly attach to this fault, and the one-line refusal script the driver can use.

FAULT REFERENCE (typical 4-cyl sedan economics, adjust for vehicle given)
- vacuum_leak: cracked/disconnected vacuum hose, PCV hose or intake gasket leaking unmetered air. Evidence: positive fuel trims concentrated at idle, low MAF, slightly high idle RPM, higher intake manifold pressure. Fix: find leak (DIY visual + carb-cleaner spray test $5, or shop smoke test $60-120); hose $5-20 DIY; intake gasket $150-350 shop. Trap: "needs a new intake manifold" or full "fuel system service" ($200-400) — trims are a symptom, not the cause.
- dirty_maf: contaminated mass-airflow sensor under-reads airflow at all speeds. Evidence: MAF low vs RPM/load everywhere, trims +10-15% at all speeds (not just idle). Fix: MAF cleaner spray $10, 15 min DIY; replacement sensor $80-250 only if cleaning fails. Trap: immediate sensor replacement at $350+ labor included, or "throttle body service" bundle.
- air_filter_restriction: clogged engine air filter choking airflow. Evidence: more throttle for same load, MAF a bit low, sluggish acceleration; trims near normal. Fix: air filter $15-30, 5 min DIY, no tools. Trap: being charged $50-90 labor for a 5-minute filter swap; "induction cleaning service".
- egr_stuck_open: EGR valve stuck open, exhaust gas diluting idle mixture. Evidence: commanded EGR pegged high, unstable idle RPM, mild positive trims. Fix: clean EGR valve $10 + 1-2h DIY (carbon removal); replacement $150-400. Trap: "full decarbonization service" $400+ when only the valve needs cleaning.
- fuel_pump_weak: pump can't hold pressure under demand. Evidence: trims normal at idle but +15-20% only under high load. Fix: confirm with fuel pressure gauge test $0-50; pump assembly $150-350 part, 1-3h labor. Trap: replacing injectors or "fuel system flush" first — the load-only trim pattern points at delivery pressure, not injectors.
- injector_leak_rich: injector dripping fuel, mixture rich. Evidence: NEGATIVE fuel trims (computer pulling fuel), high downstream O2 voltage, fuel smell. Fix: injector ohm/leak-down test; single injector $60-150 + 1h labor; don't replace full set unless multiple fail. Trap: "all six injectors must be replaced as a set" — they don't.
- ignition_misfire: weak/no spark in one cylinder (coil or plug). Evidence: RPM unstable at idle with high variance, O2 swinging, catalyst temp elevated (unburned fuel burning in the cat). Flashing CEL = stop driving, it cooks the catalytic converter ($1000+). Fix: swap coil to another cylinder to confirm ($0), spark plug $5-25 DIY 30min, coil $40-100 DIY 20min. Trap: "tune-up package" with injector cleaning $300-600 for what is one $50 coil.
- spark_plug_wear: plugs aging, efficiency slowly degrading. Evidence: long-term fuel trim climbing slowly over weeks, slightly rough idle. Fix: full plug set $20-80, 1h DIY on most 4-cyl. Trap: plugs+coils+wires "while we're in there" tripling the bill when only plugs are due.
- thermostat_stuck_open: engine never reaches operating temperature. Evidence: coolant plateaus ~60-70C after a long drive (should be 85-95C), weak cabin heat, worse fuel economy. Fix: thermostat $15-40 part, 1-2h DIY or $150-250 shop. Trap: "radiator replacement" or "head gasket inspection" — a low steady temp is the opposite signature of those.
- overheating (thermostat stuck closed / blocked flow): coolant climbing steadily past 105C. STOP DRIVING — warped head/head gasket is a $1500-3000 mistake. Fix: tow or cool-down drive to shop; thermostat $150-250; water pump $300-600 if it's the pump. Trap: none of this justifies an engine replacement quote without a compression/leak test first.
- cooling_fan_failure: radiator fan not engaging — overheats only when stationary, cools when moving. Evidence: coolant rises at idle/traffic, falls at speed. Fix: check fan fuse/relay $5-15 DIY first; fan motor $80-200 + 1h. Trap: "new radiator + fan assembly" $600+ when it's a $10 relay.
- low_coolant: air in system / leak causing erratic temperature swings and spikes. Fix: top up coolant $15 and find the leak — pressure test $30-60; hose $20-50. Trap: stop-leak additive upsells; head-gasket scare quotes without a combustion-gas test.
- catalyst_degradation: catalytic converter worn out, downstream O2 oscillating like upstream. Evidence: downstream O2 swinging instead of steady, P0420. Fix FIRST rule out the cheap causes: exhaust leak check $0-30, O2 sensor $50-150 — a tired sensor fakes this code. Real cat: aftermarket $300-900, OEM $1000-2500. Trap: instant $2000 OEM cat quote without checking sensors/leaks; "the law requires OEM" (it doesn't, CARB-compliant aftermarket is legal in most states).
- catalyst_restriction: clogged cat choking exhaust flow. Evidence: high load + low MAF + poor acceleration + catalyst temp high. Fix: backpressure test $50-100 confirms; then cat replacement as above. Trap: chasing "engine performance problems" with tune-up parts when it's exhaust backpressure.
- evap_purge_stuck: EVAP purge valve stuck open, fuel vapor flooding idle, worst right after refueling. Evidence: purge duty pegged, positive trims at idle, P0441. Fix: purge valve $20-60, 20-30min DIY (usually two clips and a hose). Trap: "gas cap + full EVAP system smoke test + charcoal canister" $500 bundle for a $30 valve.
- o2_sensor_drift: upstream O2 sensor aging, slowly biasing mixture. Evidence: long-term trim drifting over weeks/months, sluggish O2 response, slow MPG decline. Fix: upstream O2 sensor $50-150, 30min DIY with a $10 socket. Trap: replacing all 2-4 sensors at once "as a set" — only the failed one is needed.
- o2_sensor_stuck: O2 sensor flatlined (voltage stuck high or low, zero variance). Same fix economics as drift. The flat line is the tell — a live sensor always oscillates. Trap: "fuel system cleaning" to fix a dead sensor reading.
- alternator_failure: charging system dying — system voltage sagging from 14.x toward 12.x while driving. The battery is being drained to run the car; it will strand the driver soon. Fix: battery/alternator test free at most parts stores; alternator $150-400 part + 1-2h; check belt first $20-60. Trap: "new battery" alone — a battery the alternator can't charge dies again in days; you'll buy both anyway plus a tow.
- voltage_regulator_high: overcharging at 15V+, cooking the battery and popping bulbs. Usually means alternator (regulator is internal on most cars). Same economics as alternator_failure. Urgent-ish: sustained overvoltage kills electronics. Trap: chasing individual blown components without fixing the source voltage.
- map_sensor_fault: manifold pressure sensor reading nonsense (e.g. atmospheric pressure at high RPM/throttle). Computer fuels blind. Fix: check connector/vacuum line $0, sensor $40-120, 15min DIY. Trap: "drivability diagnostic package" $300+ for a sensor swap.
- tps_sensor_stuck: throttle position sensor frozen while RPM moves. Fix: connector check $0; TPS $30-100 where serviceable, 30min; on drive-by-wire, throttle body $200-500 — but verify with live data first. Trap: full throttle body replacement on a car where the TPS is a $40 bolt-on.
- healthy: all signals nominal. Say so plainly, tell them what was checked, and what the normal numbers mean. Do not invent problems. Trap section becomes: what a shop might *claim* is wrong with a healthy car (induction cleaning, flushes "by mileage") and how to decline.

WORKED EXAMPLE A
(Driver asks: "The engine shakes at idle and the light is flashing." Predictor: ignition_misfire 0.84. Evidence: RPM std 142 at idle, O2 swinging 0.2-0.9V, STFT +7%, catalyst temp 705C.)
1. WHAT'S HAPPENING — One of your engine's cylinders is skipping beats. Your idle speed is jumping around (RPM swinging ±140 where ±20 is normal) and unburned fuel is hitting your exhaust — that's why the light is FLASHING, not just on. The shake you feel is the engine literally limping.
2. ROOT CAUSE — Most likely a failed ignition coil or worn spark plug on one cylinder (84% confidence). The oxygen sensor swinging wildly plus your catalytic converter running at 705°C (about 100° hotter than normal) both point at raw fuel from a dead cylinder, not a fuel-supply problem.
3. WHAT TO DO — A flashing light means treat this now, not next month:
   - Stop driving hard; keep revs low and get it looked at within days, not weeks. Every mile of flashing-light driving cooks your catalytic converter (a $1,000+ part).
   - Free test: swap the suspect coil with a neighboring cylinder's — if the misfire follows it, that coil is your answer. Any shop does this in 15 minutes; DIY is four bolts.
   - Spark plug: $5–25, 30 min DIY. Ignition coil: $40–100, 20 min DIY. Shop total for either: $120–220.
4. WATCH OUT FOR — The classic upsell here is a "complete tune-up and fuel injection service" at $300–600. Your data shows an ignition problem, not a fuel problem — the fuel trims are nearly normal. Say: "The misfire is isolated to one cylinder with normal fuel trims — please test the coil and plug on that cylinder first."

WORKED EXAMPLE B
(Driver asks: "Is it safe to keep driving?" Predictor: thermostat_stuck_open 0.71. Evidence: coolant steady at 63C after 25 min, ambient 18C, trims normal, heater complaint.)
1. WHAT'S HAPPENING — Your engine is running cold. After 25 minutes of driving the coolant is sitting at 63°C when it should be near 90°C. That's also exactly why your heater feels weak — cabin heat is borrowed engine heat.
2. ROOT CAUSE — Almost certainly a thermostat stuck open (71% confidence): it's a $20 spring-loaded valve that's supposed to close while the engine warms up, and yours is letting coolant circulate full-time. Everything else (fuel trims, temperature stability) looks normal, which rules out the scarier cooling problems.
3. WHAT TO DO — Yes, it's safe to drive short-term; it costs you fuel economy and engine wear, not a breakdown:
   - Thermostat: part $15–40. DIY 1–2 hours with basic tools and a coolant drain pan, or $150–250 at a shop including coolant.
   - Fix it within a few weeks — long-term cold running dilutes oil and wears the engine faster.
4. WATCH OUT FOR — A low, steady temperature is the cheap problem. If a shop quotes a radiator, water pump, or "head gasket inspection" for this, walk away — those failures cause overheating or unstable temps, the opposite of your data. Say: "The coolant is steady at 63 degrees — that's a stuck-open thermostat. Please quote me for that."

WORKED EXAMPLE C
(Driver asks: "Failed my emissions test, what now?" Predictor: catalyst_degradation 0.58, o2_sensor_drift 0.25. Evidence: downstream O2 oscillating 0.25-0.80V with std 0.19 (healthy ~0.04), trims normal, P0420, 2008 Toyota Corolla, 212,000 mi.)
1. WHAT'S HAPPENING — The sensor that sits AFTER your catalytic converter is swinging up and down (0.25–0.80V) when it should read nearly flat. That swing is the converter failing to do its job of smoothing out the exhaust — which is exactly what an emissions test catches, and exactly what code P0420 means.
2. ROOT CAUSE — At 212,000 miles, a worn-out catalytic converter is the most likely cause — but confidence here is moderate (58%), and there are two cheaper culprits that fake this exact signature: a small exhaust leak near the sensor, and a lazy oxygen sensor (25% on the predictor). Rule those out before spending converter money.
3. WHAT TO DO — In this order, cheapest first:
   - Exhaust leak check: free-to-$30 visual/listen test at any muffler shop. A pinhole leak upstream of the sensor causes false P0420s.
   - Downstream O2 sensor: $50–150 part, 30-minute DIY with a $10 sensor socket. On a 17-year-old car this sensor is suspect at this mileage anyway.
   - Only if both check out: aftermarket CARB-compliant converter, $300–900 installed for this Corolla. You do NOT need the $1,800 dealer OEM unit.
4. WATCH OUT FOR — The instant "$1,800–2,500 OEM catalytic converter" quote without anyone testing the sensor or checking for leaks. Also the claim that "the law requires an original-manufacturer cat" — aftermarket CARB-compliant converters are legal in most states. Say: "Before quoting a converter, please verify the downstream O2 sensor response and check for exhaust leaks — P0420 has cheaper causes."

CALIBRATION NOTES
- If the predictor's top fault is healthy/no_fault: reassure plainly, summarize the normal readings (coolant in range, trims near zero, steady voltage, quiet O2), and do not manufacture concerns. The WATCH OUT FOR section then covers services shops sell to healthy cars: induction cleaning, transmission flushes "by mileage", lifetime-fluid replacements at low mileage, wallet-flush "maintenance packages".
- If two faults are plausible (top probability under ~60%), name both, and make step one of WHAT TO DO the cheapest action that distinguishes them.
- If severity reads mild (small deviations, no DTC set), frame it as "caught early" — the entire value of this tool is fixing a $30 problem before it becomes a $900 one. Give the watch-for threshold that means it has worsened.
- Match urgency words to physics: flashing CEL or climbing coolant = today; charging system sagging = this week, carry jumper cables; emissions/efficiency faults = this month; healthy = nothing owed.
"""


def load_env():
    env = Path(".env")
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


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
    parts = [f"{c}={tail[c].mean():.2f}" for c in CHANNELS]
    return ", ".join(parts)


def sim_predictor(fault, severity, rng):
    base = {"mild": 0.55, "moderate": 0.72, "severe": 0.86}[severity]
    top = min(0.95, max(0.40, base + rng.uniform(-0.07, 0.07)))
    others = CONFUSABLES.get(fault, [])
    rest = 1 - top
    out = [(fault if fault != "healthy" else "no_fault", round(top, 2))]
    for i, c in enumerate(others[:2]):
        share = rest * (0.6 if i == 0 else 0.3)
        out.append((c, round(share, 2)))
    return out


def build_prompt(w, meta, rng):
    vehicle, engine, miles_range = VEHICLES[rng.randrange(len(VEHICLES))]
    miles = rng.randrange(*miles_range) // 1000 * 1000
    fault = meta["fault_class"]
    pool = GENERIC_QUESTIONS + SYMPTOM_QUESTIONS.get(fault, [])
    question = pool[rng.randrange(len(pool))]
    preds = sim_predictor(fault, meta["severity"], rng)
    pred_txt = ", ".join(f"{n}: {p:.0%}" for n, p in preds)
    dtc = meta["ground_truth_dtc"] or "none"
    prompt = f"""VEHICLE: {vehicle}, {engine}, {miles:,} mi
DRIVE WINDOW: last {len(w) / 60:.1f} min, context: {meta['driving_context']}

SENSOR SUMMARY (full window):
{window_stats(w)}

LAST 30 SECONDS (averages): {last30(w)}

ACTIVE DTCs: {dtc}
PREDICTOR OUTPUT: {pred_txt}

DRIVER ASKS: {question}"""
    return prompt, question


def build_examples(df, windows_per_session, questions_per_window, rng):
    examples = []
    for sid, g in df.groupby("session_id", sort=True):
        g = g.sort_values("t").reset_index(drop=True)
        meta = {"fault_class": g["fault_class"].iat[0], "severity": g["severity"].iat[0],
                "driving_context": g["driving_context"].iat[0],
                "ground_truth_dtc": "" if pd.isna(g["ground_truth_dtc"].iat[0]) else g["ground_truth_dtc"].iat[0]}
        n, w_len = len(g), 150
        offsets = np.linspace(0, n - w_len, windows_per_session).astype(int)
        for wi, off in enumerate(offsets):
            w = g.iloc[off:off + w_len]
            for qi in range(questions_per_window):
                ex_id = f"{sid}_w{wi}_q{qi}"
                prompt, _ = build_prompt(w, meta, rng)
                examples.append({"id": ex_id, "prompt": prompt, **meta})
    return examples


def usage_cost(usage, price_mult=1.0, write_mult=1.25):
    cw = usage.cache_creation_input_tokens or 0
    cr = usage.cache_read_input_tokens or 0
    return price_mult * (usage.input_tokens * IN_PRICE + cw * IN_PRICE * write_mult
                         + cr * IN_PRICE * CACHE_READ_MULT
                         + usage.output_tokens * OUT_PRICE) / 1e6


def prewarm(client):
    """Write the system prompt into the 1h cache so batch requests can read it."""
    try:
        r = client.messages.create(
            model=MODEL,
            max_tokens=0,
            system=[{"type": "text", "text": TEACHER_SYSTEM,
                     "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
            messages=[{"role": "user", "content": "warmup"}],
        )
        return usage_cost(r.usage, write_mult=2.0)
    except Exception as e:
        print(f"[prewarm skipped: {e}]")
        return 0.0


def batch_params(prompt):
    return {
        "model": MODEL,
        "max_tokens": 2000,
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": "medium"},
        "system": [{"type": "text", "text": TEACHER_SYSTEM,
                    "cache_control": {"type": "ephemeral", "ttl": "1h"}}],
        "messages": [{"role": "user", "content": prompt}],
    }


def run_batches(client, todo, out_path, args, usage_tot):
    spent = 0.0
    cost_per_ex = 0.016  # prior from smoke test at batch prices; remeasured per chunk
    remaining = list(todo)
    n_ok = n_err = chunk_no = 0
    with out_path.open("a") as f:
        while remaining:
            affordable = int((args.max_cost - spent) / cost_per_ex)
            if affordable < 1:
                print(f"\nBudget cap ${args.max_cost:.0f} reached (${spent:.2f} spent). "
                      f"{len(remaining)} examples left ungenerated — rerun later to resume.")
                break
            chunk_no += 1
            size = min(len(remaining), affordable, 300 if chunk_no == 1 else args.chunk_size)
            chunk, remaining = remaining[:size], remaining[size:]
            spent += prewarm(client)
            batch = client.messages.batches.create(requests=[
                {"custom_id": ex["id"], "params": batch_params(ex["prompt"])} for ex in chunk
            ])
            print(f"Chunk {chunk_no}: batch {batch.id} submitted ({len(chunk)} requests), polling...")
            while True:
                b = client.messages.batches.retrieve(batch.id)
                if b.processing_status == "ended":
                    break
                print(f"  ...{b.request_counts.processing} processing, "
                      f"{b.request_counts.succeeded} done", flush=True)
                time.sleep(30)
            by_id = {ex["id"]: ex for ex in chunk}
            chunk_cost, ok = 0.0, 0
            for result in client.messages.batches.results(batch.id):
                if result.result.type != "succeeded":
                    n_err += 1
                    continue
                msg = result.result.message
                text = "".join(bl.text for bl in msg.content if bl.type == "text")
                ex = by_id[result.custom_id]
                f.write(json.dumps({
                    "id": ex["id"], "fault_class": ex["fault_class"], "severity": ex["severity"],
                    "messages": [
                        {"role": "system", "content": STUDENT_SYSTEM},
                        {"role": "user", "content": ex["prompt"]},
                        {"role": "assistant", "content": text},
                    ],
                }) + "\n")
                ok += 1
                chunk_cost += usage_cost(msg.usage, price_mult=0.5, write_mult=2.0)
                usage_tot["in"] += msg.usage.input_tokens
                usage_tot["out"] += msg.usage.output_tokens
                usage_tot["cw"] += msg.usage.cache_creation_input_tokens or 0
                usage_tot["cr"] += msg.usage.cache_read_input_tokens or 0
            f.flush()
            n_ok += ok
            spent += chunk_cost
            if ok:
                cost_per_ex = chunk_cost / ok
            print(f"Chunk {chunk_no} done: {ok} ok. Cost ${chunk_cost:.2f} "
                  f"(${cost_per_ex:.4f}/example). Total ${spent:.2f} / ${args.max_cost:.0f}. "
                  f"Generated {n_ok}, remaining {len(remaining)}")
    return n_ok, n_err, spent


def call_teacher(client, prompt):
    response = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        thinking={"type": "adaptive"},
        output_config={"effort": "medium"},
        system=[{"type": "text", "text": TEACHER_SYSTEM, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text")
    return text, response.usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/synthetic/synthetic_sessions.csv")
    ap.add_argument("--out", default="data/distilled/train.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="cap number of API calls (0 = all)")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--batch", action="store_true", help="use the Batch API (50%% off)")
    ap.add_argument("--max-cost", type=float, default=80.0, help="hard budget cap in USD (batch mode)")
    ap.add_argument("--chunk-size", type=int, default=2400, help="batch chunk size after the first")
    ap.add_argument("--windows-per-session", type=int, default=3)
    ap.add_argument("--questions-per-window", type=int, default=3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    df = pd.read_csv(args.data)
    examples = build_examples(df, args.windows_per_session, args.questions_per_window, rng)
    rng.shuffle(examples)
    print(f"Assembled {len(examples)} candidate examples "
          f"({args.windows_per_session} windows x {args.questions_per_window} questions per session)")

    if args.dry_run:
        ex = examples[0]
        print(f"\n--- example {ex['id']} ({ex['fault_class']}/{ex['severity']}) ---\n")
        print(ex["prompt"])
        print(f"\n--- teacher system prompt: {len(TEACHER_SYSTEM):,} chars ---")
        return

    load_env()
    import anthropic
    client = anthropic.Anthropic(max_retries=5)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        with out_path.open() as f:
            for line in f:
                try:
                    done.add(json.loads(line)["id"])
                except (json.JSONDecodeError, KeyError):
                    pass
    todo = [e for e in examples if e["id"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"{len(done)} already done, {len(todo)} to generate")
    if not todo:
        return

    usage_tot = {"in": 0, "out": 0, "cw": 0, "cr": 0}

    if args.batch:
        n_ok, n_err, spent = run_batches(client, todo, out_path, args, usage_tot)
        print(f"\nDone: {n_ok} ok, {n_err} failed -> {out_path}")
        print(f"Tokens: in={usage_tot['in']:,} cache_write={usage_tot['cw']:,} "
              f"cache_read={usage_tot['cr']:,} out={usage_tot['out']:,}")
        print(f"Actual cost (batch prices): ${spent:.2f}")
        return

    lock = threading.Lock()
    n_ok = n_err = 0

    def work(ex):
        text, usage = call_teacher(client, ex["prompt"])
        record = {
            "id": ex["id"], "fault_class": ex["fault_class"], "severity": ex["severity"],
            "messages": [
                {"role": "system", "content": STUDENT_SYSTEM},
                {"role": "user", "content": ex["prompt"]},
                {"role": "assistant", "content": text},
            ],
        }
        return record, usage

    with out_path.open("a") as f, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(work, ex): ex for ex in todo}
        for fut in as_completed(futures):
            ex = futures[fut]
            try:
                record, usage = fut.result()
            except Exception as e:
                n_err += 1
                print(f"[err] {ex['id']}: {e}")
                continue
            with lock:
                f.write(json.dumps(record) + "\n")
                f.flush()
                usage_tot["in"] += usage.input_tokens
                usage_tot["out"] += usage.output_tokens
                usage_tot["cw"] += usage.cache_creation_input_tokens or 0
                usage_tot["cr"] += usage.cache_read_input_tokens or 0
                n_ok += 1
                if n_ok % 25 == 0:
                    print(f"  {n_ok}/{len(todo)} done (cache reads so far: {usage_tot['cr']:,} tok)")

    cost = (usage_tot["in"] * IN_PRICE + usage_tot["cw"] * IN_PRICE * CACHE_WRITE_MULT
            + usage_tot["cr"] * IN_PRICE * CACHE_READ_MULT + usage_tot["out"] * OUT_PRICE) / 1e6
    print(f"\nDone: {n_ok} ok, {n_err} failed -> {out_path}")
    print(f"Tokens: in={usage_tot['in']:,} cache_write={usage_tot['cw']:,} "
          f"cache_read={usage_tot['cr']:,} out={usage_tot['out']:,}")
    print(f"Estimated cost: ${cost:.2f}")
    if usage_tot["cr"] == 0 and n_ok > args.workers:
        print("WARNING: zero cache reads — system prompt may be below the 4096-token cache minimum.")


if __name__ == "__main__":
    main()
