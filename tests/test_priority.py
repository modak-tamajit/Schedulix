import unittest

from algorithms.priority import schedule_priority
from core.metrics import calculate_metrics
from models.process import Process


class PriorityTests(unittest.TestCase):
    def test_non_preemptive_priority_and_tie(self):
        processes, chart = schedule_priority([Process("P1", 0, 3, 2, order=0), Process("P2", 0, 2, 1, order=1), Process("P3", 0, 1, 1, order=2)])
        calculate_metrics(processes, chart)
        self.assertEqual(chart, [(0, 2, "P2"), (2, 3, "P3"), (3, 6, "P1")])
        self.assertEqual([p.completion_time for p in processes], [6, 2, 3])

    def test_preemptive_higher_priority_arrival(self):
        processes, chart = schedule_priority([Process("P1", 0, 5, 3, order=0), Process("P2", 2, 2, 1, order=1)], True)
        calculate_metrics(processes, chart)
        self.assertEqual(chart, [(0, 2, "P1"), (2, 4, "P2"), (4, 7, "P1")])
        self.assertEqual([p.completion_time for p in processes], [7, 4])
        self.assertEqual([p.waiting_time for p in processes], [2, 0])
