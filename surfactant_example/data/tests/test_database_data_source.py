from unittest import TestCase

from force_bdss.api import DataValue

from surfactant_example.surfactant_plugin import SurfactantPlugin


class TestDatabaseDataSource(TestCase):

    def setUp(self):
        self.plugin = SurfactantPlugin()
        self.factory = self.plugin.data_source_factories[5]
        self.data_source = self.factory.create_data_source()
        self.model = self.factory.create_model()

    def test_basic_function(self):

        in_slots = self.data_source.slots(self.model)[0]
        self.assertEqual(1, len(in_slots))

        input_values = ['Water']
        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, input_values)
        ]

        res = self.data_source.run(self.model, data_values)
        self.assertEqual(1, len(res))

        ingredient = res[0].value
        self.assertEqual('Water', ingredient.name)

    def test_model_input_mode(self):

        self.model.input_mode = 'Model'
        self.model.name = 'Water'

        in_slots = self.data_source.slots(self.model)[0]
        self.assertEqual(0, len(in_slots))

        res = self.data_source.run(self.model, [])
        self.assertEqual(1, len(res))

        ingredient = res[0].value
        self.assertEqual('Water', ingredient.name)

        self.model.input_mode = 'Parameter'

        in_slots = self.data_source.slots(self.model)[0]
        self.assertEqual(1, len(in_slots))

        input_values = ['Sodium Chloride']
        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, input_values)
        ]

        res = self.data_source.run(self.model, data_values)
        self.assertEqual(1, len(res))

        ingredient = res[0].value
        self.assertEqual('Sodium Chloride', ingredient.name)
