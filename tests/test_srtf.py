import unittest

from algorithms.srtf import schedule_srtf
from core.metrics import calculate_metrics
from models.process import Process


class SRTFTests(unittest.TestCase):
    def test_arrival_preempts_longer_job(self):
        processes, chart = schedule_srtf([Process("P1", 0, 8, 1, order=0), Process("P2", 2, 2, 1, order=1)])
        calculate_metrics(processes, chart)
        self.assertEqual(chart, [(0, 2, "P1"), (2, 4, "P2"), (4, 10, "P1")])
        self.assertEqual([p.completion_time for p in processes], [10, 4])
        self.assertEqual([p.waiting_time for p in processes], [2, 0])
        self.assertEqual([p.response_time for p in processes], [0, 0])

    def test_equal_remaining_does_not_fake_switch(self):
        _, chart = schedule_srtf([Process("P1", 0, 4, 1), Process("P2", 1, 3, 1, order=1)])
        self.assertEqual(chart, [(0, 4, "P1"), (4, 7, "P2")])
