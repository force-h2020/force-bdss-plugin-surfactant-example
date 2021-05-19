from unittest import TestCase

from surfactant_example.simulation.simulation_utilities import (
    calculate_n_mols
)


class TestSurfactantUtilities(TestCase):

    def test_calculate_n_mols(self):

        n_mols = calculate_n_mols(
            1000, [0.1, 0.6, 0.3]
        )
        self.assertEqual([100, 600, 300], list(n_mols))

        n_mols = calculate_n_mols(
            10, [0.12, 0.61, 0.27]
        )
        self.assertEqual([1, 7, 2], list(n_mols))

        with self.assertRaises(AssertionError):
            calculate_n_mols(
                10, [0.05, 0.65, 0.3]
            )
        with self.assertRaises(AssertionError):
            calculate_n_mols(
                1000, [0.1, 0.2, 0.3]
            )
        with self.assertRaises(AssertionError):
            calculate_n_mols(
                1000, [0.2, 0.9, -0.1]
            )
