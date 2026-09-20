import random
import unittest

from src.baselines import run_earliest_infection


def path_graph(n):
    return {i: set(j for j in (i - 1, i + 1) if 0 <= j < n) for i in range(n)}


class TestEarliestInfectionBaseline(unittest.TestCase):
    def test_uses_observed_frontier_without_future_outbreak(self):
        result = run_earliest_infection(
            path_graph(5), {0}, beta=1.0, K=1, rng=random.Random(1)
        )

        self.assertEqual(result["plan"], [2])
        self.assertEqual(result["infected_count"], 2)


if __name__ == "__main__":
    unittest.main()
