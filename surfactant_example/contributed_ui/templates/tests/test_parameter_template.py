from unittest import TestCase

from surfactant_example.contributed_ui.surfactant_contributed_ui import (
    SURFACTANT_PLUGIN_ID
)
from surfactant_example.contributed_ui.templates import \
    ParameterTemplate


class TestParameterTemplate(TestCase):

    def setUp(self):

        self.parameter_template = ParameterTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID + '.factory.surfactant_mco',
            name='chemical',
            parameter_type='Fixed',
            value=12.0
        )

    def test___init__(self):
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.surfactant_mco"
            ".parameter.fixed",
            self.parameter_template.id
        )
        self.assertEqual('Fixed', self.parameter_template.parameter_type)
        self.assertEqual(12.0, self.parameter_template.value)
        self.assertEqual(0.5, self.parameter_template.lower_bound)
        self.assertEqual(5.0, self.parameter_template.upper_bound)
        self.assertEqual(10, self.parameter_template.n_samples)

    def test_id(self):
        self.parameter_template.parameter_type = 'Ranged'
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.surfactant_mco"
            ".parameter.ranged",
            self.parameter_template.id
        )

        self.parameter_template.plugin_id = (
            'force.bdss.surfactant.plugin.v1.factory.mco'
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.v1.factory.mco"
            ".parameter.ranged",
            self.parameter_template.id
        )

    def test_create_template(self):

        template = self.parameter_template.create_template()
        self.assertIn('id', template)
        self.assertIn('model_data', template)
        self.assertEqual(
            self.parameter_template.id,
            template['id']
        )
        self.assertDictEqual(
            {'name': 'chemical_conc',
             'type': 'CONCENTRATION',
             'value': 12},
            template['model_data']
        )

        self.parameter_template.parameter_type = 'Ranged'
        template = self.parameter_template.create_template()
        self.assertDictEqual(
            {'name': 'chemical_conc',
             'type': 'CONCENTRATION',
             'lower_bound': 0.5,
             'upper_bound': 5.0,
             'n_samples': 10},
            template['model_data']
        )

        self.parameter_template.parameter_type = 'Listed'
        template = self.parameter_template.create_template()
        self.assertDictEqual(
            {'name': 'chemical_conc',
             'type': 'CONCENTRATION',
             'levels': [0.5, 1.0, 3.0]},
            template['model_data']
        )
