from __future__ import annotations

import os
import tempfile
import unittest

from core.data_io import export_workload, get_academic_workload, get_sample_workload, import_workload
from models.process import Process


class DataIOTests(unittest.TestCase):
    def test_sample_and_academic_workloads(self) -> None:
        sample = get_sample_workload()
        self.assertEqual(len(sample), 4)
        self.assertEqual(sample[0].pid, "P1")
        self.assertEqual(sample[0].arrival_time, 0)
        self.assertEqual(sample[0].burst_time, 5)
        self.assertEqual(sample[0].priority, 2)

        academic = get_academic_workload()
        self.assertEqual(len(academic), 5)
        self.assertEqual(academic[4].pid, "P5")
        self.assertEqual(academic[4].burst_time, 2)

    def test_json_export_and_import(self) -> None:
        workload = [
            Process("P1", arrival_time=0, burst_time=4, priority=2, order=0),
            Process("P2", arrival_time=1, burst_time=3, priority=1, order=1),
        ]
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            export_workload(workload, temp_path)
            loaded = import_workload(temp_path)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].pid, "P1")
            self.assertEqual(loaded[0].arrival_time, 0)
            self.assertEqual(loaded[0].burst_time, 4)
            self.assertEqual(loaded[0].priority, 2)
            self.assertEqual(loaded[1].pid, "P2")
            self.assertEqual(loaded[1].burst_time, 3)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_csv_export_and_import(self) -> None:
        workload = [
            Process("P1", arrival_time=0, burst_time=5, priority=1, order=0),
            Process("P2", arrival_time=2, burst_time=2, priority=3, order=1),
        ]
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tf:
            temp_path = tf.name

        try:
            export_workload(workload, temp_path)
            loaded = import_workload(temp_path)
            self.assertEqual(len(loaded), 2)
            self.assertEqual(loaded[0].pid, "P1")
            self.assertEqual(loaded[0].arrival_time, 0)
            self.assertEqual(loaded[0].burst_time, 5)
            self.assertEqual(loaded[1].pid, "P2")
            self.assertEqual(loaded[1].arrival_time, 2)
            self.assertEqual(loaded[1].burst_time, 2)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_validation_errors(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            txt_path = tf.name
        try:
            with self.assertRaises(ValueError):
                export_workload([], txt_path)
            with self.assertRaises(ValueError):
                import_workload(txt_path)
        finally:
            if os.path.exists(txt_path):
                os.remove(txt_path)


if __name__ == "__main__":
    unittest.main()
