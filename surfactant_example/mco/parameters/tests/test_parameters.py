from unittest import TestCase, mock

from force_bdss.api import BaseMCOFactory

from surfactant_example.mco.parameters.ingredient import (
    IngredientMCOParameter,
    IngredientMCOParameterFactory,
)


class TestCategoricalMCOParameter(TestCase):
    def setUp(self):
        self.mco_factory = mock.Mock(
            spec=BaseMCOFactory,
            plugin_id="pid",
            plugin_name="Plugin",
            id="mcoid",
        )
        self.factory = IngredientMCOParameterFactory(self.mco_factory)
        self.default_ingredients = ["chemical1", "chemical2"]
        self.parameter = IngredientMCOParameter(
            self.factory, categories=self.default_ingredients
        )

    def test_default(self):
        self.assertListEqual(
            self.default_ingredients, self.parameter.categories
        )

    def test_sample_values(self):
        self.assertListEqual(
            self.default_ingredients, self.parameter.sample_values
        )
        self.parameter.categories.append("new_chemical")
        self.assertListEqual(
            self.default_ingredients + ["new_chemical"],
            self.parameter.sample_values,
        )

    def test_parameter_view(self):
        view = self.parameter.default_traits_view()
        self.assertEqual(
            "Ingredients", view.content.content[0].content[0].label
        )

    def test_factory_descriptions(self):
        self.assertIn(
            "A categorical parameter defining a chemical ingredient.",
            self.factory.get_description(),
        )
        self.assertEqual("Ingredient Parameter", self.factory.get_name())
        self.assertEqual("ingredient", self.factory.get_identifier())
