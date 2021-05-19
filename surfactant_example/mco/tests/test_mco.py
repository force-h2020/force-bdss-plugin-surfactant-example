from unittest import TestCase, mock

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import (
    FixedMCOParameterFactory,
    ListedMCOParameterFactory,
    RangedMCOParameterFactory,
    FixedMCOParameter,
    ListedMCOParameter,
    RangedMCOParameter,
)

from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.mco.mco import parameter_grid_generator, get_labels
from surfactant_example.mco.parameters.ingredient import (
    IngredientMCOParameter,
    IngredientMCOParameterFactory,
)


class TestMCO(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.mco_factories[0]
        self.mco = self.factory.create_optimizer()
        self.model = self.factory.create_model()

        self.parameters = [
            IngredientMCOParameter(
                mock.Mock(spec=IngredientMCOParameterFactory),
                categories=["A", "B"],
            ),
            FixedMCOParameter(
                mock.Mock(spec=FixedMCOParameterFactory), value=12.0
            ),
            ListedMCOParameter(
                mock.Mock(spec=ListedMCOParameterFactory), levels=[0.1, 2.5]
            ),
            RangedMCOParameter(
                mock.Mock(spec=RangedMCOParameterFactory),
                upper_bound=1.5,
                n_samples=3,
            ),
        ]

    def test_parameter_grid_generator(self):

        expected = [
            ("A", 12, 0.1, 0.1),
            ("A", 12, 0.1, 0.8),
            ("A", 12, 0.1, 1.5),
            ("A", 12, 2.5, 0.1),
            ("A", 12, 2.5, 0.8),
            ("A", 12, 2.5, 1.5),
            ("B", 12, 0.1, 0.1),
            ("B", 12, 0.1, 0.8),
            ("B", 12, 0.1, 1.5),
            ("B", 12, 2.5, 0.1),
            ("B", 12, 2.5, 0.8),
            ("B", 12, 2.5, 1.5),
        ]

        for index, parameter in enumerate(
            parameter_grid_generator(self.parameters)
        ):
            self.assertEqual(expected[index][:-1], parameter[:-1])
            self.assertAlmostEqual(expected[index][-1], parameter[-1])

    def test_get_labels(self):

        label_dict = get_labels(self.parameters)

        self.assertDictEqual({"A": 1, "B": 2}, label_dict)
