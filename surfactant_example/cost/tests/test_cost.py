from unittest import TestCase

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from surfactant_example.surfactant_plugin import SurfactantPlugin
from surfactant_example.tests.probe_classes.probe_formulations import (
    ProbeFormulation,
)


class TestCostDataSource(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[4]
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()

        self.formulation = ProbeFormulation()
        self.input = [self.formulation]

    def test_basic_function(self):

        in_slots = self.data_source.slots(self.model)[0]

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, self.input)
        ]

        with self.assertTraitChanges(self.model, "event", count=1):
            res = self.data_source.run(self.model, data_values)

        self.assertEqual(20.4225, res[0].value)

    def test_update_price(self):

        self.formulation.ingredients[0].price = 1000

        in_slots = self.data_source.slots(self.model)[0]
        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, self.input)
        ]

        res = self.data_source.run(self.model, data_values)

        self.assertAlmostEqual(128.422499999, res[0].value)

    def test_notify_pass_mark(self):
        pass_mark = True

        with self.assertTraitChanges(self.model, "event", count=1):
            self.model.notify_pass_mark(pass_mark)
