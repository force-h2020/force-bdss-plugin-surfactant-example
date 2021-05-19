from unittest import TestCase

from traits.testing.unittest_tools import UnittestTools

from force_bdss.api import DataValue

from surfactant_example.surfactant_plugin import SurfactantPlugin


class TestViscosityDataSource(TestCase, UnittestTools):
    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[2]
        self.data_source = self.factory.create_data_source()

    def test_basic_function(self):
        model = self.factory.create_model()
        in_slots = self.data_source.slots(model)[0]
        values = [0.4]

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]

        with self.assertTraitChanges(model, "event", count=1):
            res = self.data_source.run(model, data_values)

        self.assertAlmostEqual(res[0].value, 0.97175857038, 6)

    def test_notify_pass_mark(self):
        model = self.factory.create_model()
        pass_mark = True

        with self.assertTraitChanges(model, "event", count=1):
            model.notify_pass_mark(pass_mark)
