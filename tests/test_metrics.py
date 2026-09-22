from __future__ import annotations

import unittest

from core.metrics import calculate_metrics
from models.process import Process


class MetricsTests(unittest.TestCase):
    def test_metrics_calculation_simple(self) -> None:
        p1 = Process("P1", arrival_time=0, burst_time=4, priority=1)
        p1.start_time = 0
        p1.completion_time = 4

        p2 = Process("P2", arrival_time=2, burst_time=3, priority=2)
        p2.start_time = 4
        p2.completion_time = 7

        segments = [(0, 4, "P1"), (4, 7, "P2")]
        summary = calculate_metrics([p1, p2], segments)

        # Hand calculations:
        # P1: TAT = 4 - 0 = 4, WT = 4 - 4 = 0, RT = 0 - 0 = 0
        self.assertEqual(p1.turnaround_time, 4)
        self.assertEqual(p1.waiting_time, 0)
        self.assertEqual(p1.response_time, 0)

        # P2: TAT = 7 - 2 = 5, WT = 5 - 3 = 2, RT = 4 - 2 = 2
        self.assertEqual(p2.turnaround_time, 5)
        self.assertEqual(p2.waiting_time, 2)
        self.assertEqual(p2.response_time, 2)

        # Averages:
        # Avg WT = (0 + 2) / 2 = 1.0
        # Avg TAT = (4 + 5) / 2 = 4.5
        # Avg RT = (0 + 2) / 2 = 1.0
        self.assertAlmostEqual(summary.average_waiting_time, 1.0)
        self.assertAlmostEqual(summary.average_turnaround_time, 4.5)
        self.assertAlmostEqual(summary.average_response_time, 1.0)

        # Total time = 7, Busy = 7 -> CPU utilization = 100%
        self.assertEqual(summary.total_time, 7)
        self.assertAlmostEqual(summary.cpu_utilization, 100.0)
        # Throughput = 2 / 7
        self.assertAlmostEqual(summary.throughput, 2 / 7)

    def test_metrics_with_idle_time(self) -> None:
        p1 = Process("P1", arrival_time=2, burst_time=3, priority=1)
        p1.start_time = 2
        p1.completion_time = 5

        segments = [(0, 2, "IDLE"), (2, 5, "P1")]
        summary = calculate_metrics([p1], segments)

        # P1: TAT = 5 - 2 = 3, WT = 3 - 3 = 0, RT = 2 - 2 = 0
        self.assertEqual(p1.turnaround_time, 3)
        self.assertEqual(p1.waiting_time, 0)
        self.assertEqual(p1.response_time, 0)

        # Total time = 5, Busy = 3 -> CPU util = 3/5 * 100 = 60.0%
        self.assertEqual(summary.total_time, 5)
        self.assertAlmostEqual(summary.cpu_utilization, 60.0)
        self.assertAlmostEqual(summary.throughput, 1 / 5)


if __name__ == "__main__":
    unittest.main()
