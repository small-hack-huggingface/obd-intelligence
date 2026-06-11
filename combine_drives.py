"""
Combine every real_drive_*.csv in a folder into one clean dataset.

Handles the two gotchas:
  1. Each file's `timestamp` restarts at 0.0 (it's seconds-since-start of that
     run). We keep that as `t_in_drive` and build a continuous global `timestamp`
     by offsetting each drive after the previous one.
  2. We tag every row with `source_drive` so you never lose track of which run a
     row came from (useful for per-drive feature windows later).

Then it prints the refreshed .describe() table — paste those ranges into the
REAL dict at the top of generate_dataset.py to re-ground the synthetic states.

    python combine_drives.py                 # scans current folder
    python combine_drives.py --dir data      # scan a specific folder
"""
import argparse
import glob
import os
import pandas as pd

SIGNALS = ["rpm", "speed_kph", "coolant_temp_c", "engine_load_pct",
           "throttle_pct", "intake_temp_c"]
GAP_SECONDS = 1.0  # small gap inserted between drives in the global clock


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=".", help="folder to scan for real_drive_*.csv")
    ap.add_argument("--out", default="combined_drives.csv")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "real_drive_*.csv")))
    if not files:
        print(f"No real_drive_*.csv found in {os.path.abspath(args.dir)}")
        return
    print(f"Found {len(files)} drive(s):")
    for f in files:
        print("  -", os.path.basename(f))

    frames = []
    offset = 0.0
    for f in files:
        df = pd.read_csv(f)
        df["t_in_drive"] = df["timestamp"]
        df["source_drive"] = os.path.basename(f).replace(".csv", "")
        df["timestamp"] = df["t_in_drive"] + offset      # continuous global clock
        offset = df["timestamp"].max() + GAP_SECONDS
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    cols = ["timestamp", "t_in_drive", "source_drive"] + SIGNALS
    combined = combined[[c for c in cols if c in combined.columns]]
    combined.to_csv(args.out, index=False)

    total_min = combined["timestamp"].max() / 60
    print(f"\nWrote {len(combined)} rows across {len(files)} drives "
          f"(~{total_min:.1f} min total) -> {args.out}")

    # quick data-quality check: flag any all-empty columns
    empties = [c for c in SIGNALS if c in combined and combined[c].isna().all()]
    if empties:
        print("WARNING - these columns are entirely empty (car may not expose them):", empties)

    print("\n--- refreshed stats (paste these ranges into generate_dataset.py REAL dict) ---")
    desc = combined[SIGNALS].describe(percentiles=[.05, .25, .5, .75, .95])
    pd.set_option("display.width", 140, "display.max_columns", 20)
    print(desc.round(1))


if __name__ == "__main__":
    main()