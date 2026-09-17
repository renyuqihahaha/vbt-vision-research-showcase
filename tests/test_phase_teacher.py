import unittest

from src.phase_teacher import Observation, Phase, audit_trajectory, infer_phases


class PhaseTeacherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sequence = [
            Observation(0.0, 100.0),
            Observation(0.5, 130.0),
            Observation(1.0, 170.0),
            Observation(1.5, 192.0),
            Observation(2.0, 192.0),
            Observation(2.5, 160.0),
            Observation(3.0, 120.0),
            Observation(3.5, 100.0),
        ]

    def test_quality_gate_accepts_clear_motion(self) -> None:
        report = audit_trajectory(self.sequence)
        self.assertTrue(report.accepted)
        self.assertEqual(report.rom_px, 92.0)

    def test_quality_gate_rejects_low_confidence(self) -> None:
        sequence = [Observation(i * 0.5, 100.0 + i, 0.1) for i in range(5)]
        report = audit_trajectory(sequence)
        self.assertFalse(report.accepted)
        self.assertIn("insufficient_tracking_confidence", report.reasons)

    def test_phase_sequence_contains_descent_and_ascent(self) -> None:
        phases = infer_phases(self.sequence)
        self.assertIn(Phase.DESCENDING, phases)
        self.assertIn(Phase.BOTTOM, phases)
        self.assertIn(Phase.ASCENDING, phases)


if __name__ == "__main__":
    unittest.main()
