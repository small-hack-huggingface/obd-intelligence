"""Connect to the ELM327 emulator and read sample PIDs.

Start the emulator first (separate terminal):
    elm327-emulator -s car -n 35000

Then run:
    python obd_connection.py              # stream sample PIDs
    python obd_connection.py --discover   # list all supported queries + sample values

Environment:
    conda activate small-hack-1
"""

from __future__ import annotations

import argparse
import os
import time

import obd

# TCP port must match the emulator's -n flag (default dev setup: 35000).
EMULATOR_PORT = os.getenv("OBD_PORT", "socket://localhost:35000")

# Default streaming set for feature extraction / smoke tests.
PIDS = [
    obd.commands.RPM,
    obd.commands.SPEED,
    obd.commands.COOLANT_TEMP,
    obd.commands.ENGINE_LOAD,
    obd.commands.MAF,
    obd.commands.INTAKE_PRESSURE,
    obd.commands.INTAKE_TEMP,
    obd.commands.SHORT_FUEL_TRIM_1,
    obd.commands.LONG_FUEL_TRIM_1,
    obd.commands.THROTTLE_POS,
    obd.commands.TIMING_ADVANCE,
]


def connect(port: str = EMULATOR_PORT) -> obd.OBD:
    """Open a python-OBD session to the emulator."""
    connection = obd.OBD(
        portstr=port,
        baudrate=38400,  # skip auto-baud probe (\x7f bytes) — not needed over TCP
        check_voltage=False,  # emulator does not report real battery voltage
        timeout=30,
    )
    if not connection.is_connected():
        raise ConnectionError(
            f"Could not connect to {port}. "
            "Is the emulator running? (elm327-emulator -s car -n 35000)"
        )
    return connection


def read_sample(connection: obd.OBD, pids: list | None = None) -> dict[str, object | None]:
    """Query each PID once and return values."""
    targets = pids or PIDS
    sample: dict[str, object | None] = {}
    for pid in targets:
        response = connection.query(pid)
        sample[pid.name] = None if response.is_null() else response.value
    return sample


def discover(connection: obd.OBD) -> list[dict[str, str]]:
    """Query every command the connection reports as supported."""
    results: list[dict[str, str]] = []
    for cmd in sorted(connection.supported_commands, key=lambda c: c.name):
        response = connection.query(cmd)
        if response.is_null():
            value = "NULL"
        else:
            value = str(response.value)
        results.append(
            {
                "name": cmd.name,
                "description": cmd.desc,
                "value": value,
            }
        )
    return results


def print_discover(connection: obd.OBD) -> None:
    rows = discover(connection)
    print(f"Supported queries: {len(rows)}\n")
    print(f"{'Command':<32} {'Sample value':<28} Description")
    print("-" * 100)
    for row in rows:
        print(f"{row['name']:<32} {row['value']:<28} {row['description']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="OBD emulator connection sample")
    parser.add_argument(
        "--discover",
        action="store_true",
        help="list all supported queries and sample values from the emulator",
    )
    args = parser.parse_args()

    print(f"Connecting to {EMULATOR_PORT} ...")
    connection = connect()
    print(f"Status: {connection.status()}")

    if args.discover:
        print_discover(connection)
    else:
        print("\nSingle read:")
        print(read_sample(connection))

        print("\nStreaming 10 samples (~1 Hz):")
        for i in range(10):
            print(f"  [{i + 1:02d}] {read_sample(connection)}")
            time.sleep(1)

    connection.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
