from unittest import TestCase, mock

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import (
    KPISpecification,
    Workflow,
    DataValue,
    FixedMCOParameterFactory,
    ListedMCOParameterFactory,
    RangedMCOParameterFactory,
    FixedMCOParameter,
    ListedMCOParameter,
    RangedMCOParameter,
)
from force_nevergrad.mco.ng_mco_model import NevergradMCOModel
from force_nevergrad.mco.ng_mco import NevergradMCO

from surfactant_example.mco.surfactant_nevergrad_mco.ng_mco_factory import (
    NevergradMCOFactory,
)
from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.mco.parameters.ingredient import (
    IngredientMCOParameter,
    IngredientMCOParameterFactory,
)


class TestMCO(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.mco_factories[1]
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
        self.model.parameters = self.parameters

    def test_mco_model(self):
        self.assertEqual("TwoPointsDE", self.model.algorithms)
        self.assertEqual(100, self.model.budget)
        self.assertEqual(True, self.model.verbose_run)

    def test_mco_factory(self):
        self.assertIsInstance(self.factory, NevergradMCOFactory)
        self.assertEqual(
            "surfactant_nevergrad_mco", self.factory.get_identifier()
        )
        self.assertIs(self.factory.get_model_class(), NevergradMCOModel)
        self.assertIs(self.factory.get_optimizer_class(), NevergradMCO)
        self.assertEqual(4, len(self.factory.get_parameter_factory_classes()))

    def test_simple_run(self):
        mco = self.factory.create_optimizer()
        model = self.factory.create_model()
        model.budget = 61
        model.parameters = self.parameters
        model.kpis = [KPISpecification(), KPISpecification()]

        evaluator = Workflow()

        evaluator.mco_model = model
        kpis = [DataValue(value=1), DataValue(value=2)]
        with self.assertTraitChanges(model, "event", count=61):
            with mock.patch(
                "force_bdss.api.Workflow.execute", return_value=kpis
            ) as mock_exec:
                mco.run(evaluator)
                self.assertEqual(76, mock_exec.call_count)
