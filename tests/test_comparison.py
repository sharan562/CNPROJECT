import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.comparison import load_config, parse_arguments, run_trials, summarize_trials


class TestTrialSummary(unittest.TestCase):
    def test_trials_use_the_requested_seed_nodes(self):
        graph = {"A": {"B"}, "B": {"A"}}
        results = run_trials(graph, seeds=["A"], beta=1.0, trial_count=2)
        self.assertEqual(results["No Containment"], [2, 2])

    def test_summary_reports_mean_and_zero_interval_for_identical_results(self):
        summary = summarize_trials({"Proposed": [4, 4, 4]})

        self.assertEqual(summary["Proposed"]["trials"], 3)
        self.assertEqual(summary["Proposed"]["mean_final_infected"], 4)
        self.assertEqual(summary["Proposed"]["ci95_half_width"], 0.0)

    def test_load_config_reads_values_from_a_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "config.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump({
                    "topology": "data/bank_topology_multibranch.json",
                    "seed_node": "WS_N1",
                    "beta": 0.4,
                    "budget": 2,
                    "trials": 5,
                    "random_seed": 7,
                }, file)

            config = load_config(path)
            self.assertEqual(config["topology"], "data/bank_topology_multibranch.json")
            self.assertEqual(config["seed_node"], "WS_N1")
            self.assertEqual(config["beta"], 0.4)
            self.assertEqual(config["budget"], 2)

    def test_parse_arguments_prioritizes_cli_over_config(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "config.json")
            with open(path, "w", encoding="utf-8") as file:
                json.dump({
                    "topology": "data/bank_topology.json",
                    "seed_node": "WS_1",
                    "beta": 0.25,
                    "budget": 2,
                    "trials": 30,
                    "random_seed": 42,
                }, file)

            with patch("sys.argv", ["prog", "--config", path, "--beta", "0.9", "--budget", "4"]):
                args = parse_arguments()

            self.assertEqual(args.topology, "data/bank_topology.json")
            self.assertEqual(args.seed_node, "WS_1")
            self.assertEqual(args.beta, 0.9)
            self.assertEqual(args.budget, 4)
            self.assertEqual(args.trials, 30)
            self.assertEqual(args.random_seed, 42)

    def test_parse_arguments_allows_a_custom_output_directory(self):
        with patch("sys.argv", ["prog", "--output-dir", "results/custom"]):
            args = parse_arguments()

        self.assertEqual(args.output_dir, "results/custom")


if __name__ == "__main__":
    unittest.main()
