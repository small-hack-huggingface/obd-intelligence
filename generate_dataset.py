"""Generate labeled synthetic OBD-II training sessions grounded in real drive data.

Real channels (rpm, speed, coolant, load, throttle, intake temp) are sampled as
contiguous windows from actual drive recordings (combined_drives.csv), so the
dynamics are real. The remaining PIDs are derived with physical couplings, then
fault signatures from docs/fault_simulation.md are injected at mild / moderate /
severe levels.

    python generate_dataset.py --real data/real/combined_drives.csv \
        --out data/synthetic/synthetic_sessions.csv
"""
import argparse

import numpy as np
import pandas as pd

REAL_SIGNALS = ["rpm", "speed_kph", "coolant_temp_c", "engine_load_pct",
                "throttle_pct", "intake_temp_c"]

# Observed ranges from combined_drives.csv (refresh via combine_drives.py)
REAL = {
    "rpm": (520, 3130),
    "speed_kph": (0, 116),
    "coolant_temp_c": (86, 90),
    "engine_load_pct": (0, 100),
    "throttle_pct": (12.5, 52.5),
    "intake_temp_c": (29, 61),
}

SEVERITY = {"mild": 0.6, "moderate": 1.0, "severe": 1.4}


# ---------------------------------------------------------------- carrier ----

def load_drives(path):
    df = pd.read_csv(path)
    df["sec"] = df["t_in_drive"].astype(int)
    per_sec = (df.groupby(["source_drive", "sec"])[REAL_SIGNALS]
                 .mean().reset_index())
    return [g.reset_index(drop=True) for _, g in per_sec.groupby("source_drive")]


def w_any(w):       return True
def w_idleish(w):   return (w["speed_kph"] < 5).mean() > 0.15
def w_highload(w):  return (w["engine_load_pct"] > 60).mean() > 0.10
def w_moving(w):    return w["speed_kph"].mean() > 20


def pick_window(drives, need, n_sec, rng):
    lengths = np.array([len(d) for d in drives], dtype=float)
    window = None
    for _ in range(80):
        d = drives[rng.choice(len(drives), p=lengths / lengths.sum())]
        if len(d) <= n_sec:
            continue
        start = rng.integers(0, len(d) - n_sec)
        window = d.iloc[start:start + n_sec]
        if need(window):
            break
    return window[REAL_SIGNALS].reset_index(drop=True).copy()


def augment(df, rng):
    n = len(df)
    df["rpm"] = df["rpm"] * rng.uniform(0.96, 1.05) + rng.normal(0, 15, n)
    df["speed_kph"] = np.clip(df["speed_kph"] + rng.normal(0, 0.5, n), 0, None)
    df["coolant_temp_c"] = df["coolant_temp_c"] + rng.normal(0, 0.3, n)
    df["engine_load_pct"] = np.clip(
        df["engine_load_pct"] * rng.uniform(0.95, 1.05) + rng.normal(0, 1, n), 0, 100)
    df["throttle_pct"] = np.clip(df["throttle_pct"] + rng.normal(0, 0.4, n), 0, 100)
    df["intake_temp_c"] = df["intake_temp_c"] + rng.uniform(-3, 3) + rng.normal(0, 0.5, n)
    return df


# ------------------------------------------------------- derived channels ----

def derive(df, rng):
    n = len(df)
    t = np.arange(n)
    baro = 97 + rng.normal(0, 0.5)
    df["baro_kpa"] = round(baro, 1)

    ve = 0.15 + 0.0075 * df["engine_load_pct"]
    df["maf_gps"] = np.clip((df["rpm"] / 60) * ve * 1.184 + rng.normal(0, 0.3, n), 0.5, None)
    df["map_kpa"] = np.clip(28 + 0.62 * df["engine_load_pct"] + rng.normal(0, 1.5, n), 18, baro)

    df["stft_pct"] = rng.normal(0, 1.2, n) + 1.5 * np.sin(t / 7 + rng.uniform(0, 6))
    walk = np.cumsum(rng.normal(0, 0.05, n))
    df["ltft_pct"] = np.clip(rng.normal(0, 1.0) + walk - walk.mean(), -6, 6)

    df["o2_b1s2_v"] = np.clip(0.62 + 0.04 * np.sin(t / 11) + rng.normal(0, 0.025, n), 0, 1.1)

    idle = (df["speed_kph"] < 5).astype(float)
    df["control_module_voltage_v"] = 14.25 - 0.25 * idle + rng.normal(0, 0.05, n)

    df["timing_advance_deg"] = np.clip(
        10 + 0.009 * df["rpm"] - 0.10 * df["engine_load_pct"] + rng.normal(0, 1, n), 2, 45)

    cat_target = 320 + 3.0 * df["engine_load_pct"] + 0.06 * df["rpm"]
    df["catalyst_temp_c"] = cat_target.ewm(alpha=0.03).mean() + rng.normal(0, 3, n)

    cruise = (df["speed_kph"] > 30) & df["engine_load_pct"].between(15, 65)
    df["commanded_egr_pct"] = np.where(cruise, np.clip(8 + rng.normal(0, 1.5, n), 0, 20), 0.0)
    df["evap_purge_pct"] = np.where(cruise, np.clip(18 + rng.normal(0, 4, n), 0, 40), 0.0)
    return df


# ------------------------------------------------------------ fault model ----
# Signatures and magnitudes follow docs/fault_simulation.md; `s` scales severity.

def f_healthy(df, s, rng):
    pass


def f_vacuum_leak(df, s, rng):
    idle = df["speed_kph"] < 5
    df.loc[idle, "stft_pct"] += 20 * s
    df.loc[idle, "ltft_pct"] += 15 * s
    df.loc[~idle, "stft_pct"] += 8 * s
    df.loc[~idle, "ltft_pct"] += 6 * s
    df.loc[idle, "maf_gps"] *= (1 - 0.30 * s)
    df.loc[idle, "map_kpa"] += 10 * s
    df.loc[idle, "rpm"] += 80 * s


def f_dirty_maf(df, s, rng):
    df["maf_gps"] *= (1 - 0.35 * s)
    df["stft_pct"] += 12 * s
    df["ltft_pct"] += 10 * s


def f_air_filter(df, s, rng):
    df["throttle_pct"] = np.clip(df["throttle_pct"] + 15 * s, 0, 100)
    df["maf_gps"] *= (1 - 0.15 * s)
    df["engine_load_pct"] *= (1 - 0.10 * s)


def f_egr_stuck(df, s, rng):
    df["commanded_egr_pct"] = np.clip(60 + 30 * s + rng.normal(0, 3, len(df)), 0, 100)
    idle = df["speed_kph"] < 5
    df.loc[idle, "rpm"] += rng.normal(0, 120 * s, int(idle.sum()))
    df["stft_pct"] += 8 * s


def f_fuel_pump(df, s, rng):
    load = df["engine_load_pct"] > 60
    df.loc[load, "stft_pct"] += 20 * s
    df.loc[load, "ltft_pct"] += 14 * s


def f_injector_rich(df, s, rng):
    df["stft_pct"] -= 18 * s
    df["ltft_pct"] -= 12 * s
    df["o2_b1s2_v"] = np.clip(df["o2_b1s2_v"] + 0.15 * s, 0, 1.1)


def f_misfire(df, s, rng):
    n = len(df)
    idle = df["speed_kph"] < 5
    df.loc[idle, "rpm"] += rng.normal(0, 150 * s, int(idle.sum()))
    drops = rng.random(n) < 0.05
    df.loc[drops, "rpm"] -= 200 * s
    df["o2_b1s2_v"] = np.clip(df["o2_b1s2_v"] + rng.normal(0, 0.12 * s, n), 0, 1.1)
    df["stft_pct"] += 6 * s
    df["catalyst_temp_c"] += 60 * s


def f_spark_wear(df, s, rng):
    ramp = np.linspace(0, 1, len(df))
    df["ltft_pct"] += 4 + (10 * s - 4) * ramp
    df["stft_pct"] += 3 * s


def f_thermostat_open(df, s, rng):
    n = len(df)
    df["coolant_temp_c"] = 70 - 8 * s + 2 * np.sin(np.arange(n) / 40) + rng.normal(0, 0.6, n)


def f_overheat(df, s, rng):
    n = len(df)
    df["coolant_temp_c"] = 90 + (15 + 12 * s) * np.linspace(0, 1, n) + rng.normal(0, 0.5, n)


def f_fan_failure(df, s, rng):
    temp = np.empty(len(df))
    cur = 88.0
    idle = (df["speed_kph"] < 5).to_numpy()
    for i in range(len(df)):
        cur += 0.08 * s if idle[i] else -0.04 * (cur - 88)
        temp[i] = cur
    df["coolant_temp_c"] = temp + rng.normal(0, 0.4, len(df))


def f_low_coolant(df, s, rng):
    n = len(df)
    x = np.zeros(n)
    for i in range(1, n):
        x[i] = 0.9 * x[i - 1] + rng.normal(0, 2.5 * s)
    spikes = (rng.random(n) < 0.03) * rng.uniform(5, 12, n) * s
    df["coolant_temp_c"] += x + spikes


def f_catalyst_deg(df, s, rng):
    n = len(df)
    t = np.arange(n)
    df["o2_b1s2_v"] = np.clip(
        0.45 + 0.25 * s * np.sin(t / 3 + rng.uniform(0, 6)) + rng.normal(0, 0.08 * s, n), 0, 1.1)


def f_catalyst_restrict(df, s, rng):
    df["maf_gps"] *= (1 - 0.20 * s)
    df["engine_load_pct"] = np.clip(df["engine_load_pct"] + 15 * s, 0, 100)
    df["catalyst_temp_c"] += 120 * s
    df["throttle_pct"] = np.clip(df["throttle_pct"] + 8 * s, 0, 100)


def f_evap_purge(df, s, rng):
    df["evap_purge_pct"] = np.clip(60 + 30 * s + rng.normal(0, 4, len(df)), 0, 100)
    idle = df["speed_kph"] < 5
    df.loc[idle, "stft_pct"] += 14 * s
    df.loc[idle, "ltft_pct"] += 6 * s


def f_o2_drift(df, s, rng):
    n = len(df)
    df["ltft_pct"] += np.linspace(0, 10 * s, n)
    df["o2_b1s2_v"] = 0.62 + rng.normal(0, 0.008, n)


def f_o2_stuck(df, s, rng):
    level = 0.05 if rng.random() < 0.5 else 0.90
    df["o2_b1s2_v"] = level + rng.normal(0, 0.004, len(df))


def f_alternator(df, s, rng):
    n = len(df)
    df["control_module_voltage_v"] = (14.3 - 1.8 * s * np.linspace(0, 1, n)
                                      + rng.normal(0, 0.06, n))


def f_regulator_high(df, s, rng):
    df["control_module_voltage_v"] = 15.2 + 0.5 * s + rng.normal(0, 0.08, len(df))


def f_map_fault(df, s, rng):
    df["map_kpa"] = 94 + rng.normal(0, 2, len(df))


def f_tps_stuck(df, s, rng):
    df["throttle_pct"] = 15 + rng.normal(0, 0.3, len(df))


FAULTS = {
    "healthy":               dict(fn=f_healthy,           dtc=None,    need=w_any),
    "vacuum_leak":           dict(fn=f_vacuum_leak,       dtc="P0171", need=w_idleish),
    "dirty_maf":             dict(fn=f_dirty_maf,         dtc="P0101", need=w_moving),
    "air_filter_restriction": dict(fn=f_air_filter,       dtc=None,    need=w_moving),
    "egr_stuck_open":        dict(fn=f_egr_stuck,         dtc="P0401", need=w_idleish),
    "fuel_pump_weak":        dict(fn=f_fuel_pump,         dtc="P0171", need=w_highload),
    "injector_leak_rich":    dict(fn=f_injector_rich,     dtc="P0172", need=w_any),
    "ignition_misfire":      dict(fn=f_misfire,           dtc="P0301", need=w_idleish),
    "spark_plug_wear":       dict(fn=f_spark_wear,        dtc=None,    need=w_any),
    "thermostat_stuck_open": dict(fn=f_thermostat_open,   dtc="P0128", need=w_any),
    "overheating":           dict(fn=f_overheat,          dtc="P0217", need=w_any),
    "cooling_fan_failure":   dict(fn=f_fan_failure,       dtc=None,    need=w_idleish),
    "low_coolant":           dict(fn=f_low_coolant,       dtc=None,    need=w_any),
    "catalyst_degradation":  dict(fn=f_catalyst_deg,      dtc="P0420", need=w_moving),
    "catalyst_restriction":  dict(fn=f_catalyst_restrict, dtc="P0420", need=w_highload),
    "evap_purge_stuck":      dict(fn=f_evap_purge,        dtc="P0441", need=w_idleish),
    "o2_sensor_drift":       dict(fn=f_o2_drift,          dtc="P0136", need=w_any),
    "o2_sensor_stuck":       dict(fn=f_o2_stuck,          dtc="P0136", need=w_any),
    "alternator_failure":    dict(fn=f_alternator,        dtc="P0562", need=w_any),
    "voltage_regulator_high": dict(fn=f_regulator_high,   dtc="P0563", need=w_any),
    "map_sensor_fault":      dict(fn=f_map_fault,         dtc="P0106", need=w_moving),
    "tps_sensor_stuck":      dict(fn=f_tps_stuck,         dtc="P0122", need=w_moving),
}


# ------------------------------------------------------------------ build ----

def clip_physical(df):
    df["rpm"] = df["rpm"].clip(400, 6500)
    df["coolant_temp_c"] = df["coolant_temp_c"].clip(-40, 125)
    df["stft_pct"] = df["stft_pct"].clip(-25, 25)
    df["ltft_pct"] = df["ltft_pct"].clip(-25, 25)
    df["control_module_voltage_v"] = df["control_module_voltage_v"].clip(10, 16)
    df["catalyst_temp_c"] = df["catalyst_temp_c"].clip(100, 950)
    return df


def context_of(df):
    mean_speed = df["speed_kph"].mean()
    if mean_speed < 8:
        return "idle"
    return "city" if mean_speed < 45 else "highway"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--real", default="data/real/combined_drives.csv")
    ap.add_argument("--out", default="data/synthetic/synthetic_sessions.csv")
    ap.add_argument("--summary-out", default="data/synthetic/sessions_summary.csv")
    ap.add_argument("--sessions-per-class", type=int, default=25)
    ap.add_argument("--seconds", type=int, default=300)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    drives = load_drives(args.real)
    print(f"Loaded {len(drives)} real drive(s): {[len(d) for d in drives]} sec each")

    frames, summary = [], []
    for fault, spec in FAULTS.items():
        for i in range(args.sessions_per_class):
            severity = rng.choice(list(SEVERITY), p=[0.30, 0.45, 0.25])
            s = SEVERITY[severity]
            df = pick_window(drives, spec["need"], args.seconds, rng)
            df = augment(df, rng)
            df = derive(df, rng)
            spec["fn"](df, s, rng)
            df = clip_physical(df).round(2)

            sid = f"{fault}_{i:03d}"
            dtc = spec["dtc"] if (spec["dtc"] and severity != "mild") else ""
            ctx = context_of(df)
            df.insert(0, "t", np.arange(len(df)))
            df.insert(0, "ground_truth_dtc", dtc)
            df.insert(0, "driving_context", ctx)
            df.insert(0, "severity", severity)
            df.insert(0, "fault_class", fault)
            df.insert(0, "session_id", sid)
            frames.append(df)
            summary.append(dict(session_id=sid, fault_class=fault, severity=severity,
                                driving_context=ctx, ground_truth_dtc=dtc,
                                seconds=len(df)))

    out = pd.concat(frames, ignore_index=True)
    out.to_csv(args.out, index=False)
    pd.DataFrame(summary).to_csv(args.summary_out, index=False)

    print(f"\nWrote {len(out):,} rows / {len(summary)} sessions -> {args.out}")
    print(f"Summary -> {args.summary_out}\n")
    print(pd.DataFrame(summary).groupby("fault_class")["severity"]
          .value_counts().unstack(fill_value=0).to_string())


if __name__ == "__main__":
    main()
