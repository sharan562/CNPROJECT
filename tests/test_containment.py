import random
import unittest

from src.containment import quarantine, contain
from src.propagation import propagate


def path_graph(n):
    """Nodes 0..n-1 connected in a line."""
    return {i: set(j for j in (i - 1, i + 1) if 0 <= j < n) for i in range(n)}


class TestQuarantine(unittest.TestCase):
    def test_removes_node_and_edges(self):
        g = {0: {1}, 1: {0, 2}, 2: {1}}
        self.assertEqual(quarantine(g, 1), {0: set(), 2: set()})

    def test_does_not_mutate_original(self):
        g = {0: {1}, 1: {0}}
        quarantine(g, 0)
        self.assertEqual(g, {0: {1}, 1: {0}})

    def test_missing_node_returns_unchanged(self):
        g = {0: {1}, 1: {0}}
        self.assertEqual(quarantine(g, 99), g)


class TestContain(unittest.TestCase):
    def test_respects_budget(self):
        g = path_graph(6)
        plan, _ = contain(g, {0}, beta=1.0, K=2, rng=random.Random(1))
        self.assertLessEqual(len(plan), 2)

    def test_reduces_infection_vs_baseline(self):
        g = path_graph(6)
        _, baseline_infected = propagate(g, {0}, beta=1.0, rng=random.Random(1))
        _, contained = contain(g, {0}, beta=1.0, K=2, rng=random.Random(1))
        self.assertLess(contained, len(baseline_infected))

    def test_no_budget_means_no_quarantine(self):
        g = path_graph(5)
        plan, count = contain(g, {0}, beta=1.0, K=0, rng=random.Random(1))
        self.assertEqual(plan, [])
        self.assertEqual(count, 5)

    def test_deterministic_given_seed(self):
        g = path_graph(6)
        p1, c1 = contain(g, {0}, beta=0.5, K=3, rng=random.Random(7))
        p2, c2 = contain(g, {0}, beta=0.5, K=3, rng=random.Random(7))
        self.assertEqual(p1, p2)
        self.assertEqual(c1, c2)

    def test_plan_nodes_are_valid(self):
        g = path_graph(6)
        plan, _ = contain(g, {0}, beta=1.0, K=2, rng=random.Random(1))
        for v in plan:
            self.assertIn(v, g)

    def test_eps_above_growth_stops_actions(self):
        g = path_graph(6)
        plan, count = contain(g, {0}, beta=1.0, K=5, eps=100.0, rng=random.Random(1))
        self.assertEqual(plan, [])
        self.assertEqual(count, 6)

    def test_picks_highest_scored_node(self):
        # 'c' bridges the hub 'b' to two extra leaves, giving it the highest
        # centrality (3/4) and reach among the still-susceptible nodes.
        g = {
            'a': {'b'},
            'b': {'a', 'c', 'd', 'e'},
            'c': {'b', 'f', 'g'},
            'd': {'b'},
            'e': {'b'},
            'f': {'c'},
            'g': {'c'},
        }
        plan, _ = contain(g, {'a'}, beta=1.0, K=1, rng=random.Random(1))
        self.assertEqual(plan, ['c'])


if __name__ == "__main__":
    unittest.main()
