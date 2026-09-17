"""Run the public phase-teacher demonstration on synthetic observations."""

from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.phase_teacher import Observation, audit_trajectory, infer_phases, phase_values


def main() -> None:
    observations = [
        Observation(0.0, 100.0),
        Observation(0.5, 130.0),
        Observation(1.0, 170.0),
        Observation(1.5, 192.0),
        Observation(2.0, 192.0),
        Observation(2.5, 160.0),
        Observation(3.0, 120.0),
        Observation(3.5, 100.0),
    ]

    quality = audit_trajectory(observations)
    phases = infer_phases(observations)

    print(f"quality.accepted={quality.accepted}")
    print(f"quality.valid_ratio={quality.valid_ratio:.2f}")
    print(f"quality.rom_px={quality.rom_px:.2f}")
    print("phases=" + ",".join(phase_values(phases)))


if __name__ == "__main__":
    main()
