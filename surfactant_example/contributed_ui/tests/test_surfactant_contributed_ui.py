from unittest import TestCase

from surfactant_example.contributed_ui.surfactant_contributed_ui import (
    SurfactantContributedUI)
from surfactant_example.data.gromacs_database import GromacsDatabase


class TestSurfactantContributedUI(TestCase):

    def setUp(self):
        self.gromacs_database = GromacsDatabase()
        self.custom_ui = SurfactantContributedUI()

    def test___init__(self):

        workflow = self.custom_ui.workflow_data["workflow"]
        self.assertIsInstance(workflow['mco_model'], dict)
        self.assertIsInstance(workflow['execution_layers'], list)
        self.assertIsInstance(workflow['notification_listeners'], list)

        self.assertEqual(
            3,
            len(self.custom_ui.execution_layers_template
                .surfactant_template_list)
        )
        self.assertEqual(
            3, self.custom_ui.execution_layers_template.n_ingredients
        )
        self.assertFalse(
            self.custom_ui.mco_template.enable_secondary_surfactant
        )

    def test_update_enable_secondary_surfactant(self):

        self.custom_ui.execution_layers_template\
            .secondary_surfactant_template = (
                self.custom_ui.execution_layers_template
                    .surfactant_template_list[2])

        self.assertEqual(
            4,
            self.custom_ui.execution_layers_template.n_ingredients
        )
        self.assertTrue(
            self.custom_ui.mco_template.enable_secondary_surfactant
        )

        self.custom_ui.execution_layers_template\
            .secondary_surfactant_template = (
                self.custom_ui.execution_layers_template
                    .empty_surfactant_template
            )
        self.assertEqual(
            3, self.custom_ui.execution_layers_template.n_ingredients
        )
        self.assertFalse(
            self.custom_ui.mco_template.enable_secondary_surfactant
        )

    def test_workflow_data(self):

        self.assertNotEqual(
            self.custom_ui._workflow_data_default(),
            self.custom_ui.workflow_data
        )
        self.custom_ui.mco_template.primary_surfactant_conc.value = 12.0

        workflow_data = self.custom_ui.workflow_data["workflow"]
        mco_data = workflow_data['mco_model']['model_data']

        self.assertEqual(
            12, mco_data['parameters'][0]['model_data']['value']
        )

        self.assertEqual(
            'sodium_dodecyl_sulfate_conc',
            mco_data['parameters'][0]['model_data']['name']
        )
        self.assertEqual(
            'sodium_chloride_conc',
            mco_data['parameters'][1]['model_data']['name']
        )
