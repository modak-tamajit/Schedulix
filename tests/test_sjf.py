import unittest

from algorithms.sjf import schedule_sjf
from core.metrics import calculate_metrics
from models.process import Process


class SJFTests(unittest.TestCase):
    def test_shortest_available_and_tie_order(self):
        processes, chart = schedule_sjf([Process("P1", 0, 4, 1, order=0), Process("P2", 0, 2, 1, order=1), Process("P3", 0, 2, 1, order=2)])
        calculate_metrics(processes, chart)
        self.assertEqual(chart, [(0, 2, "P2"), (2, 4, "P3"), (4, 8, "P1")])
        self.assertEqual([p.completion_time for p in processes], [8, 2, 4])
        self.assertEqual([p.waiting_time for p in processes], [4, 0, 2])

    def test_waits_for_arrival(self):
        _, chart = schedule_sjf([Process("P1", 3, 1, 1)])
        self.assertEqual(chart, [(0, 3, "IDLE"), (3, 4, "P1")])
