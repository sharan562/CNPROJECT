import random
import unittest

from src.baselines import (
    run_degree_quarantine,
    run_earliest_infection,
    run_random_quarantine,
)


def path_graph(n):
    return {i: set(j for j in (i - 1, i + 1) if 0 <= j < n) for i in range(n)}


class TestEarliestInfectionBaseline(unittest.TestCase):
    def test_uses_observed_frontier_without_future_outbreak(self):
        result = run_earliest_infection(
            path_graph(5), {0}, beta=1.0, K=1, rng=random.Random(1)
        )

        self.assertEqual(result["plan"], [2])
        self.assertEqual(result["infected_count"], 2)


class TestBudgetExhaustion(unittest.TestCase):
    def setUp(self):
        self.graph = {
            "seed": {"hub"},
            "hub": {"seed", "leaf_1", "leaf_2"},
            "leaf_1": {"hub"},
            "leaf_2": {"hub"},
        }

    def test_degree_baseline_continues_after_budget_is_used(self):
        result = run_degree_quarantine(
            self.graph, {"seed"}, beta=1.0, K=1, rng=random.Random(1)
        )

        self.assertEqual(len(result["plan"]), 1)
        self.assertEqual(result["infected_count"], 3)


class TestDeterministicBaselines(unittest.TestCase):
    def test_baseline_does_not_restart_after_a_failed_spread_step(self):
        result = run_random_quarantine(
            path_graph(3), {0}, beta=0.25, K=1,
            rng=random.Random(2), selection_rng=random.Random(99),
        )
        self.assertEqual(result["plan"], [])
        self.assertEqual(result["infected_count"], 1)

    def test_random_selection_does_not_advance_infection_rng(self):
        graph = path_graph(3)
        infection_rng = random.Random(42)
        expected_rng = random.Random(42)
        expected_rng.random()  # One infection attempt infects node 1.

        run_random_quarantine(
            graph,
            {0},
            beta=1.0,
            K=1,
            rng=infection_rng,
            selection_rng=random.Random(99),
        )

        self.assertEqual(infection_rng.random(), expected_rng.random())

    def test_random_baseline_is_deterministic_for_a_fixed_seed(self):
        graph = path_graph(6)
        first = run_random_quarantine(
            graph, {0}, beta=0.5, K=2, rng=random.Random(42)
        )
        second = run_random_quarantine(
            graph, {0}, beta=0.5, K=2, rng=random.Random(42)
        )

        self.assertEqual(first, second)

    def test_random_baseline_continues_after_budget_is_used(self):
        graph = {
            "seed": {"hub"},
            "hub": {"seed", "leaf_1", "leaf_2"},
            "leaf_1": {"hub"},
            "leaf_2": {"hub"},
        }
        result = run_random_quarantine(
            graph, {"seed"}, beta=1.0, K=1, rng=random.Random(1)
        )

        self.assertEqual(len(result["plan"]), 1)
        self.assertEqual(result["infected_count"], 3)


if __name__ == "__main__":
    unittest.main()
