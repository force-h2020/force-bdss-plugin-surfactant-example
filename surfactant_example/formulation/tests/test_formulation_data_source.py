from unittest import TestCase

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.formulation.formulation_data_source import (
    calculate_solvent_conc, MissingIngredientException)
from surfactant_example.tests.probe_classes.probe_ingredients import (
    ProbePrimaryIngredient, ProbeSaltIngredient, ProbeSolventIngredient
)


class TestFormulationDataSource(UnittestTools, TestCase):

    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[6]
        self.data_source = self.factory.create_data_source()

    def test_basic_function(self):

        model = self.factory.create_model()
        in_slots = self.data_source.slots(model)[0]

        self.assertEqual(5, len(in_slots))

        input_values = [
            ProbePrimaryIngredient(), 12,
            ProbeSaltIngredient(), 1.0,
            ProbeSolventIngredient()
        ]

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, input_values)
        ]

        res = self.data_source.run(model, data_values)

        self.assertEqual(1, len(res))
        self.assertEqual('FORMULATION', res[0].type)

        formulation = res[0].value
        self.assertEqual(3, len(formulation.ingredients))
        self.assertListEqual([12, 1, 87], formulation.concentrations)

    def test__check_ingredient_roles(self):
        ingredients = [
            ProbePrimaryIngredient(),
            ProbeSaltIngredient(),
            ProbeSolventIngredient()
        ]

        self.assertTrue(
            self.data_source._check_ingredient_roles(ingredients)
        )

        with self.assertRaises(MissingIngredientException):
            self.data_source._check_ingredient_roles(
                ingredients[:-1])

    def test_calculate_solvent_conc(self):
        solvent_conc = calculate_solvent_conc(
            [10, 3, 6]
        )

        self.assertEqual(81, solvent_conc)

        with self.assertRaises(AssertionError):
            calculate_solvent_conc(
                [100, 3, 6]
            )
        with self.assertRaises(AssertionError):
            calculate_solvent_conc(
                [-100, 3, 6]
            )

    def test_n_surfactants_slots(self):

        model = self.factory.create_model()

        with self.assertTraitChanges(model, 'changes_slots'):
            model.n_surfactants = 3
