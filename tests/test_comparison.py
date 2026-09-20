import unittest

from src.comparison import summarize_trials


class TestTrialSummary(unittest.TestCase):
    def test_summary_reports_mean_and_zero_interval_for_identical_results(self):
        summary = summarize_trials({"Proposed": [4, 4, 4]})

        self.assertEqual(summary["Proposed"]["trials"], 3)
        self.assertEqual(summary["Proposed"]["mean_final_infected"], 4)
        self.assertEqual(summary["Proposed"]["ci95_half_width"], 0.0)


if __name__ == "__main__":
    unittest.main()
