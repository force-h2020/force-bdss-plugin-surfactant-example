from unittest import TestCase

from surfactant_example.contributed_ui.surfactant_contributed_ui import (
    SURFACTANT_PLUGIN_ID
)
from surfactant_example.contributed_ui.templates import \
    MCOTemplate


class TestMCOTemplate(TestCase):

    def setUp(self):

        self.mco_template = MCOTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID
        )

    def test___init__(self):
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0",
            self.mco_template.plugin_id
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.surfactant_mco",
            self.mco_template.id
        )
        self.assertEqual(2, len(self.mco_template.parameter_templates))
        self.assertEqual(
            'Fixed', self.mco_template.parameter_templates[0].parameter_type
        )
        self.assertEqual(
            'primary_surfactant',
            self.mco_template.parameter_templates[0].name
        )
        self.assertEqual(
            'Ranged', self.mco_template.parameter_templates[1].parameter_type
        )
        self.assertEqual(
            'salt', self.mco_template.parameter_templates[1].name
        )
        self.assertNotIn(
            self.mco_template.secondary_surfactant_conc,
            self.mco_template.parameter_templates
        )

    def test_id(self):
        self.mco_template.mco_name = 'mco'
        new_id = "force.bdss.surfactant.plugin.example.v0.factory.mco"
        self.assertEqual(new_id, self.mco_template.id)
        self.assertEqual(
            new_id, self.mco_template.primary_surfactant_conc.plugin_id
        )
        self.assertEqual(
            new_id, self.mco_template.secondary_surfactant_conc.plugin_id
        )
        self.assertEqual(new_id, self.mco_template.salt_conc.plugin_id)

        self.mco_template.plugin_id = 'force.bdss.surfactant.plugin.v1'
        new_id = "force.bdss.surfactant.plugin.v1.factory.mco"
        self.assertEqual(new_id, self.mco_template.id)
        self.assertEqual(
            new_id, self.mco_template.primary_surfactant_conc.plugin_id
        )
        self.assertEqual(
            new_id, self.mco_template.secondary_surfactant_conc.plugin_id
        )
        self.assertEqual(new_id, self.mco_template.salt_conc.plugin_id)

    def test_create_template(self):

        template = self.mco_template.create_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            self.mco_template.id,
            template['id']
        )

        keys = list(template['model_data'].keys())
        self.assertListEqual(
            ["parameters", "kpis"],
            keys
        )
        self.assertEqual(2, len(template['model_data']['parameters']))
        self.assertEqual(2, len(template['model_data']['kpis']))

        self.assertEqual(
            'primary_surfactant_conc',
            template['model_data']['parameters'][0]['model_data']['name']
        )
        self.assertEqual(
            'salt_conc',
            template['model_data']['parameters'][1]['model_data']['name']
        )

        self.mco_template.parameter_templates = []
        template = self.mco_template.create_template()
        keys = list(template['model_data'].keys())
        self.assertListEqual(
            ["parameters", "kpis"],
            keys
        )
        self.assertEqual(0, len(template['model_data']['parameters']))
        self.assertEqual(2, len(template['model_data']['kpis']))

        self.assertEqual(
            'micelle', template['model_data']['kpis'][0]["name"]
        )
        self.assertEqual(
            'cost', template['model_data']['kpis'][1]["name"]
        )

    def test_update_secondary_surf_conc(self):
        self.mco_template.enable_secondary_surfactant = True
        self.mco_template.secondary_surfactant_conc.level = 5.0

        self.assertIn(
            self.mco_template.secondary_surfactant_conc,
            self.mco_template.parameter_templates
        )

        template = self.mco_template.create_template()
        self.assertEqual(3, len(template['model_data']['parameters']))

        self.mco_template.enable_secondary_surfactant = False
        self.assertAlmostEqual(
            1.0, self.mco_template.secondary_surfactant_conc.value)
        self.assertNotIn(
            self.mco_template.secondary_surfactant_conc,
            self.mco_template.parameter_templates
        )

        template = self.mco_template.create_template()
        self.assertEqual(2, len(template['model_data']['parameters']))
