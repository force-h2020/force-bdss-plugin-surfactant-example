from unittest import TestCase

from force_gromacs.api import GromacsFragment

from surfactant_example.formulation.formulation import (
    calculate_num_fractions)
from surfactant_example.ingredient.ingredient import Ingredient
from surfactant_example.tests.probe_classes.probe_formulations import (
    ProbeFormulation)


class TestFormulation(TestCase):

    def setUp(self):
        self.formulation = ProbeFormulation()

    def test_init_(self):
        self.assertEqual(4, len(self.formulation.ingredients))
        self.assertEqual(4, len(self.formulation.concentrations))
        self.assertEqual(4, len(self.formulation.num_fractions))
        self.assertEqual(20.4225, self.formulation.price)
        self.assertEqual('ps1-pi-12.0-ss-4.0-pi-ni-0.5',
                         self.formulation.ref)

    def test_num_fractions(self):

        expected = [0.01795212, 0.00837765,
                    0.00209441, 0.97157579]
        self.assertAlmostEqual(
            1, sum(self.formulation.num_fractions))
        for expect, value in zip(expected, self.formulation.num_fractions):
            self.assertAlmostEqual(expect, value)

    def test_calculate_num_fractions(self):
        masses = [100, 200]
        concentrations = [1, 1]

        num_frac = calculate_num_fractions(
            masses, concentrations
        )

        self.assertEqual(len(num_frac), 2)
        self.assertAlmostEqual(1, sum(num_frac))

        self.assertAlmostEqual(num_frac[0], 2/3)
        self.assertAlmostEqual(num_frac[1], 1/3)

        masses = [120, 100, 20]
        concentrations = [10, 5, 85]

        num_frac = calculate_num_fractions(
            masses, concentrations
        )

        self.assertEqual(len(num_frac), 3)
        self.assertAlmostEqual(1, sum(num_frac), 6)

        self.assertAlmostEqual(num_frac[0], 0.0190114, 5)
        self.assertAlmostEqual(num_frac[1], 0.0114068, 5)
        self.assertAlmostEqual(num_frac[2], 0.9695817, 5)

    def test_get_ref(self):
        self.formulation.concentrations[0] = 10
        self.assertEqual('ps1-pi-10.0-ss-4.0-pi-ni-0.5',
                         self.formulation.ref)

        self.formulation.ingredients[0].fragments[0].symbol = 'SDS'
        self.assertEqual('sds-pi-10.0-ss-4.0-pi-ni-0.5',
                         self.formulation.ref)

        self.formulation.ingredients[3].fragments[0].symbol = 'SOL'
        self.assertEqual('sds-pi-10.0-ss-4.0-pi-ni-0.5',
                         self.formulation.ref)

    def test_fragment_search(self):

        fragments = self.formulation.fragment_search(['PS1', 'PI'])
        self.assertEqual(2, len(fragments))
        self.assertIsInstance(fragments[0], GromacsFragment)
        self.assertIsInstance(fragments[1], GromacsFragment)

    def test_ingredient_search(self):

        surfactants = self.formulation.ingredient_search(['Surfactant'])

        self.assertEqual(2, len(surfactants))
        self.assertIsInstance(surfactants[0], Ingredient)
        self.assertIsInstance(surfactants[1], Ingredient)
