import unittest

from algorithms.round_robin import schedule_round_robin
from core.metrics import calculate_metrics
from models.process import Process


class RoundRobinTests(unittest.TestCase):
    def test_multiple_cycles_and_arrival_at_quantum_end(self):
        processes, chart = schedule_round_robin([Process("P1", 0, 5, 1, order=0), Process("P2", 2, 3, 1, order=1)], 2)
        calculate_metrics(processes, chart)
        self.assertEqual(chart, [(0, 2, "P1"), (2, 4, "P2"), (4, 6, "P1"), (6, 7, "P2"), (7, 8, "P1")])
        self.assertEqual([p.completion_time for p in processes], [8, 7])
        self.assertEqual([p.turnaround_time for p in processes], [8, 5])
        self.assertEqual([p.waiting_time for p in processes], [3, 2])

    def test_idle_and_invalid_quantum(self):
        _, chart = schedule_round_robin([Process("P1", 4, 1, 1)], 1)
        self.assertEqual(chart, [(0, 4, "IDLE"), (4, 5, "P1")])
        with self.assertRaises(ValueError): schedule_round_robin([Process("P1", 0, 1, 1)], 0)
