"""Windowed feature extraction shared by predictor training and the Space."""
import numpy as np
import pandas as pd

CHANNELS = ["rpm", "speed_kph", "coolant_temp_c", "engine_load_pct", "throttle_pct",
            "intake_temp_c", "maf_gps", "map_kpa", "stft_pct", "ltft_pct", "o2_b1s2_v",
            "control_module_voltage_v", "timing_advance_deg", "catalyst_temp_c",
            "commanded_egr_pct", "evap_purge_pct"]

STATS = ["mean", "std", "slope", "min", "max"]

FEATURE_NAMES = [f"{c}_{s}" for c in CHANNELS for s in STATS] + [
    "idle_frac", "highload_frac", "coolant_at_idle_mean", "stft_at_load_mean"]


def extract(window: pd.DataFrame) -> np.ndarray:
    """window: rows at 1 Hz with all CHANNELS columns."""
    feats = []
    n = len(window)
    dur_min = max(n / 60.0, 1e-6)
    for c in CHANNELS:
        v = window[c].to_numpy(dtype=float)
        feats += [v.mean(), v.std(), (v[-1] - v[0]) / dur_min, v.min(), v.max()]
    idle = window["speed_kph"] < 5
    load = window["engine_load_pct"] > 60
    feats.append(idle.mean())
    feats.append(load.mean())
    feats.append(window.loc[idle, "coolant_temp_c"].mean() if idle.any()
                 else window["coolant_temp_c"].mean())
    feats.append(window.loc[load, "stft_pct"].mean() if load.any()
                 else window["stft_pct"].mean())
    return np.array(feats, dtype=np.float32)
