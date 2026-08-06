from __future__ import annotations

import csv
from pathlib import Path
import random

OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(parents=True, exist_ok=True)

DELAYS = [0, 1, 2, 5, 10, 15, 20, 25, 30, 35, 40]

def write_schedule(
    name: str,
    delays: list[float],
    *,
    seed: int | None,
    role: str,
) -> None:
    path = OUT / f"{name}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "schedule",
                "position",
                "delay_ms",
                "repetition",
                "seed",
                "role",
            ],
        )
        writer.writeheader()
        counts: dict[float, int] = {}
        for position, delay in enumerate(delays, start=1):
            counts[delay] = counts.get(delay, 0) + 1
            writer.writerow(
                {
                    "schedule": name,
                    "position": position,
                    "delay_ms": delay,
                    "repetition": counts[delay],
                    "seed": "" if seed is None else seed,
                    "role": role,
                }
            )
    print(f"Wrote {len(delays)} samples to {path}")

# Independent calibration set: every delay appears twice in random order.
calibration = DELAYS * 2
calibration_rng = random.Random(77)
calibration_rng.shuffle(calibration)
write_schedule(
    "calibration_seed77",
    calibration,
    seed=77,
    role="calibration",
)

# Three randomized validation schedules.
for seed in (101, 202, 303):
    values = DELAYS * 3
    rng = random.Random(seed)
    rng.shuffle(values)
    write_schedule(
        f"randomized_seed{seed}",
        values,
        seed=seed,
        role="validation",
    )

# Abrupt shift: stable/low drift, sudden unsafe drift, then recovery.
abrupt = (
    [0, 1, 2, 5, 10] * 3
    + [25, 30, 35, 40, 30] * 3
    + [10, 5, 2, 1, 0] * 3
)
write_schedule(
    "abrupt_shift",
    abrupt,
    seed=None,
    role="validation",
)

# Hysteresis-style up/down drift.
one_cycle = [
    0, 1, 2, 5, 10, 15, 20, 25, 30, 35, 40,
    35, 30, 25, 20, 15, 10, 5, 2, 1, 0,
]
write_schedule(
    "up_down",
    one_cycle * 2,
    seed=None,
    role="validation",
)

# Untouched holdout. Do not use to choose the rolling window.
holdout = DELAYS * 3
holdout_rng = random.Random(909)
holdout_rng.shuffle(holdout)
write_schedule(
    "holdout_seed909",
    holdout,
    seed=909,
    role="holdout",
)
