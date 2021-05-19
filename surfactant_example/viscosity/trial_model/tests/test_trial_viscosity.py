from unittest import TestCase

from force_bdss.api import DataValue

from surfactant_example.tests.probe_classes.probe_formulations import (
    ProbeFormulation)

from .. trial_viscosity_model import ViscosityModelParameters
from .. trial_viscosity_data_source import SQRT2PI
from .. trial_viscosity_factory import TrialViscosityFactory


class TestModelParameters(TestCase):

    def setUp(self):

        self.model_parameters = ViscosityModelParameters(
            name='Primary Surfactant',
            mean=12.0,
            sigma=0.5
        )

    def test_init(self):
        self.assertEqual('Primary Surfactant',
                         self.model_parameters.name)
        self.assertEqual(12.0, self.model_parameters.mean)
        self.assertEqual(0.5, self.model_parameters.sigma)

    def test_get_state(self):

        self.assertDictEqual(
            {'name': 'Primary Surfactant',
             'mean': 12.0,
             'sigma': 0.5},
            self.model_parameters.__getstate__()
        )


class TestTrialViscosityDataSource(TestCase):

    def setUp(self):

        self.factory = TrialViscosityFactory(
            {'id': '0', 'name': 'dummy'}
        )
        self.formulation = ProbeFormulation()
        self.formulation.ingredients[0].name = "Primary Surfactant"
        self.formulation.ingredients[1].name = "Secondary Surfactant"
        self.formulation.ingredients[2].name = "Salt"
        self.state = {
                'ingredient_models': [
                    {'name': 'Primary Surfactant',
                     'mean': 12.0,
                     'sigma': 1.0}
                ],
                'calculation_mode': 'Sum',
                'input_slot_info': [],
                'output_slot_info': []}
        self.data_source = self.factory.create_data_source()

    def test_basic_function(self):

        model = self.factory.create_model()
        model.ingredient_models = [
            ViscosityModelParameters(
                name='Primary Surfactant',
                mean=12.0,
                sigma=1.0),
            ViscosityModelParameters(
                name='Secondary Surfactant',
                mean=4.0,
                sigma=1.0),
            ViscosityModelParameters(
                name='Salt',
                mean=0.5,
                sigma=1.0)
        ]
        in_slots = self.data_source.slots(model)[0]

        self.assertEqual(1, len(in_slots))

        values = [self.formulation]

        data_values = [
            DataValue(type=slot.type, value=value)
            for slot, value in zip(in_slots, values)
        ]

        res = self.data_source.run(model, data_values)

        self.assertAlmostEqual(
            3 / SQRT2PI, res[0].value)

    def test_get_state(self):

        # Test serialisation of model object
        model = self.factory.create_model()
        model.ingredient_models.append(
            ViscosityModelParameters(
                name='Primary Surfactant',
                mean=12.0,
                sigma=1.0
            )
        )

        self.assertDictEqual(
            self.state,
            model.__getstate__()["model_data"]
        )

    def test_model_init(self):
        # Test initialisation of model object from
        # serialised state
        model = self.factory.create_model(
            self.state)
        self.assertDictEqual(
            self.state,
            model.__getstate__()["model_data"]
        )

    def test_add_viscosity_model_button(self):
        model = self.factory.create_model()
        self.assertEqual(0, len(model.ingredient_models))
        self.assertEqual(-1, model.selected_table_index)

        model._add_viscosity_model_button_fired()
        self.assertEqual(1, len(model.ingredient_models))
        self.assertEqual(0, model.selected_table_index)

    def test_remove_viscosity_model_button_fired(self):

        model = self.factory.create_model()
        model.ingredient_models = [
            ViscosityModelParameters(name='First Model'),
            ViscosityModelParameters(name='Second Model'),
            ViscosityModelParameters(name='Third Model'),
            ViscosityModelParameters(name='Fourth Model')]

        self.assertEqual(
            'Fourth Model',
            model.ingredient_models[model.selected_table_index].name)

        model._remove_viscosity_model_button_fired()
        self.assertEqual(3, len(model.ingredient_models))
        self.assertEqual(2, model.selected_table_index)
        self.assertEqual(
            'Third Model',
            model.ingredient_models[model.selected_table_index].name)

        model.selected_table_index = 1
        model._remove_viscosity_model_button_fired()
        self.assertEqual(2, len(model.ingredient_models))
        self.assertEqual(1, model.selected_table_index)
        self.assertEqual(
            'First Model', model.ingredient_models[0].name)
        self.assertEqual(
            'Third Model',
            model.ingredient_models[model.selected_table_index].name)
