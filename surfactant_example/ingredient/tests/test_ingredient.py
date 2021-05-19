from unittest import TestCase

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from surfactant_example.tests.probe_classes.probe_ingredients import (
    ProbePrimaryIngredient,
)
from surfactant_example.tests.probe_classes.probe_fragments import (
    ProbePrimarySurfactant,
    ProbePositiveIon,
    ProbeSolvent
)
from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.ingredient import Ingredient


class TestIngredient(TestCase):
    def setUp(self):

        self.ingredient = ProbePrimaryIngredient()

    def test___init__(self):
        self.assertEqual(
            "Positive Ion Primary Surfactant", self.ingredient.name
        )
        self.assertEqual(0, self.ingredient.charge)
        self.assertTrue(self.ingredient.neutral)
        self.assertEqual(140, self.ingredient.mass)
        self.assertEqual(3, self.ingredient.atom_count)


class TestIngredientsDataSource(TestCase, UnittestTools):

    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[0]
        self.data_source = self.factory.create_data_source()

    def test_basic_function_surfactant(self):

        model = self.factory.create_model()
        model.name = "Test Ingredient"
        model.role = "Surfactant"
        model.price = 10
        model.n_fragments = 2

        input_values = [ProbePrimarySurfactant(),
                        ProbePositiveIon()]

        in_slots = self.data_source.slots(model)[0]

        self.assertEqual(2, len(in_slots))

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, input_values)
        ]

        res = self.data_source.run(model, data_values)

        self.assertEqual(1, len(res))
        self.assertEqual("INGREDIENT", res[0].type)

        ingredient = res[0].value
        self.assertIsInstance(ingredient, Ingredient)
        self.assertEqual("Test Ingredient", ingredient.name)
        self.assertEqual("Surfactant", ingredient.role)
        self.assertEqual(2, len(ingredient.fragments))
        self.assertEqual(10, ingredient.price)

    def test_basic_function_solvent(self):

        model = self.factory.create_model()
        model.name = "Test Solvent"
        model.role = "Solvent"
        model.price = 1
        model.n_fragments = 1

        input_values = [ProbeSolvent()]
        in_slots = self.data_source.slots(model)[0]

        self.assertEqual(1, len(in_slots))

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, input_values)
        ]

        with self.assertTraitChanges(model, "event", count=1):
            res = self.data_source.run(model, data_values)

        self.assertEqual(1, len(res))
        self.assertEqual("INGREDIENT", res[0].type)

        ingredient = res[0].value
        self.assertIsInstance(ingredient, Ingredient)
        self.assertEqual("Test Solvent", ingredient.name)
        self.assertEqual("Solvent", ingredient.role)
        self.assertEqual(1, len(ingredient.fragments))
        self.assertEqual(1, ingredient.price)

    def test_slots(self):

        model = self.factory.create_model()
        model.n_fragments = 2

        in_slots = self.data_source.slots(model)[0]
        self.assertEqual(model.n_fragments, len(in_slots))

        types = ["FRAGMENT", "FRAGMENT"]

        for type_, slot in zip(types, in_slots):
            self.assertEqual(type_, slot.type)

    def test_notify_ingredient(self):
        model = self.factory.create_model()
        ingredient = ProbePrimaryIngredient()

        with self.assertTraitChanges(model, "event", count=1):
            model.notify_ingredient(ingredient)
