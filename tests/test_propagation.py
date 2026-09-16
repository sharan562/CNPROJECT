import random
import unittest

from src.propagation import simulate_step, propagate


def path_graph(n):
    """Nodes 0..n-1 connected in a line."""
    return {i: set(j for j in (i - 1, i + 1) if 0 <= j < n) for i in range(n)}


class TestSimulateStep(unittest.TestCase):
    def test_beta_zero_no_spread(self):
        g = path_graph(3)
        new = simulate_step(g, {0}, beta=0.0, rng=random.Random(1))
        self.assertEqual(new, set())

    def test_beta_one_infects_susceptible_neighbors(self):
        g = path_graph(3)
        new = simulate_step(g, {0}, beta=1.0, rng=random.Random(1))
        self.assertEqual(new, {1})

    def test_already_infected_neighbor_not_reinfected(self):
        g = {0: {1}, 1: {0, 2}, 2: {1}}
        new = simulate_step(g, {0, 2}, beta=1.0, rng=random.Random(1))
        self.assertEqual(new, {1})

    def test_deterministic_given_seed(self):
        g = path_graph(5)
        rng1 = random.Random(42)
        rng2 = random.Random(42)
        self.assertEqual(simulate_step(g, {0}, 0.5, rng1),
                         simulate_step(g, {0}, 0.5, rng2))


class TestPropagate(unittest.TestCase):
    def test_arrival_time_equals_graph_distance(self):
        g = path_graph(5)
        arrival, _ = propagate(g, {0}, beta=1.0, rng=random.Random(1))
        self.assertEqual(arrival[4], 4)
        self.assertEqual(arrival[0], 0)

    def test_disconnected_component_not_infected(self):
        g = {0: {1}, 1: {0}, 2: {3}, 3: {2}}
        arrival, infected = propagate(g, {0}, beta=1.0, rng=random.Random(1))
        self.assertIn(1, arrival)
        self.assertNotIn(2, arrival)
        self.assertNotIn(3, arrival)
        self.assertEqual(infected, {0, 1})

    def test_deterministic_given_seed(self):
        g = path_graph(5)
        a1, _ = propagate(g, {0}, beta=0.5, rng=random.Random(7))
        a2, _ = propagate(g, {0}, beta=0.5, rng=random.Random(7))
        self.assertEqual(a1, a2)


if __name__ == "__main__":
    unittest.main()
