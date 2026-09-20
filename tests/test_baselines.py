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

    def test_random_baseline_continues_after_budget_is_used(self):
        result = run_random_quarantine(
            self.graph, {"seed"}, beta=1.0, K=1, rng=random.Random(1)
        )

        self.assertEqual(len(result["plan"]), 1)
        self.assertEqual(result["infected_count"], 3)


if __name__ == "__main__":
    unittest.main()
