import unittest

from algorithms.fcfs import schedule_fcfs
from core.metrics import calculate_metrics
from models.process import Process


class FCFSTests(unittest.TestCase):
    def test_arrival_order_and_idle_time(self):
        processes, chart = schedule_fcfs([Process("P1", 2, 3, 1, order=0), Process("P2", 2, 1, 2, order=1)])
        self.assertEqual(chart, [(0, 2, "IDLE"), (2, 5, "P1"), (5, 6, "P2")])
        self.assertEqual([p.completion_time for p in processes], [5, 6])
        summary = calculate_metrics(processes, chart)
        self.assertEqual((processes[0].turnaround_time, processes[1].waiting_time, processes[0].response_time), (3, 3, 0))
        self.assertEqual(summary.cpu_utilization, 4 / 6 * 100)

    def test_single_process(self):
        processes, chart = schedule_fcfs([Process("P1", 0, 4, 1)])
        calculate_metrics(processes, chart)
        self.assertEqual((processes[0].completion_time, processes[0].waiting_time, processes[0].response_time), (4, 0, 0))
