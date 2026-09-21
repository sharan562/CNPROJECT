import unittest

from src.risk_score import (
    urgency, centrality, reach, risk_score, score_all, distances_to_infected,
)


def star_graph(m):
    """Center 'c' with leaves 'l1'..'lm'."""
    g = {'c': set(f'l{i}' for i in range(1, m + 1))}
    for i in range(1, m + 1):
        g[f'l{i}'] = {'c'}
    return g


def path_graph(n):
    return {i: set(j for j in (i - 1, i + 1) if 0 <= j < n) for i in range(n)}


class TestUrgency(unittest.TestCase):
    def test_closer_is_more_urgent(self):
        self.assertGreater(urgency(0.0, tau=5.0), urgency(10.0, tau=5.0))

    def test_unreachable_is_zero(self):
        self.assertEqual(urgency(float('inf'), tau=5.0), 0.0)

    def test_bounded(self):
        for distance in (0.0, 1.0, 5.0, 100.0):
            self.assertTrue(0.0 < urgency(distance, 5.0) <= 1.0)


class TestDistancesToInfected(unittest.TestCase):
    def test_distance_to_nearest_infected(self):
        g = path_graph(5)
        self.assertEqual(distances_to_infected(g, {0}), {0: 0, 1: 1, 2: 2, 3: 3, 4: 4})

    def test_multi_source_takes_nearest(self):
        g = path_graph(5)
        self.assertEqual(distances_to_infected(g, {0, 4})[2], 2)

    def test_unreachable_not_included(self):
        g = {0: {1}, 1: {0}, 2: set()}
        self.assertEqual(distances_to_infected(g, {0}), {0: 0, 1: 1})


class TestCentrality(unittest.TestCase):
    def test_center_is_max(self):
        g = star_graph(5)
        self.assertEqual(centrality(g, 'c'), 1.0)

    def test_leaf_less_than_center(self):
        g = star_graph(5)
        self.assertLess(centrality(g, 'l1'), centrality(g, 'c'))

    def test_leaf_value(self):
        g = star_graph(5)
        self.assertAlmostEqual(centrality(g, 'l1'), 1.0 / 5.0)

    def test_empty_graph(self):
        self.assertEqual(centrality({}, 'x'), 0.0)


class TestReach(unittest.TestCase):
    def test_middle_reaches_more_than_end(self):
        g = path_graph(5)
        self.assertGreater(reach(g, 2, infected=set()), reach(g, 0, infected=set()))

    def test_end_reach_value(self):
        g = path_graph(5)
        self.assertAlmostEqual(reach(g, 0, infected=set()), 2.0 / 5.0)

    def test_isolated_node_zero(self):
        g = {0: set()}
        self.assertEqual(reach(g, 0, infected=set()), 0.0)


class TestCompositeScore(unittest.TestCase):
    def test_score_in_unit_interval(self):
        g = star_graph(5)
        infected = {'l1', 'c'}
        s = risk_score(g, 'c', infected, tau=5.0, alpha=0.4, beta=0.35, gamma=0.25)
        self.assertTrue(0.0 <= s <= 1.0)

    def test_central_infected_beats_peripheral_susceptible(self):
        g = star_graph(5)
        infected = {'l1', 'c'}
        sc = risk_score(g, 'c', infected, tau=5.0, alpha=0.4, beta=0.35, gamma=0.25)
        sl = risk_score(g, 'l2', infected, tau=5.0, alpha=0.4, beta=0.35, gamma=0.25)
        self.assertGreater(sc, sl)


class TestScoreAll(unittest.TestCase):
    def test_returns_all_nodes(self):
        g = star_graph(3)
        infected = {'l1'}
        scores = score_all(g, infected, tau=5.0, alpha=0.4, beta=0.35, gamma=0.25)
        self.assertEqual(set(scores), set(g))


if __name__ == "__main__":
    unittest.main()
