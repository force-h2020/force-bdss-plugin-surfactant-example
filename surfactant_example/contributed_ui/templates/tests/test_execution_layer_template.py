from unittest import TestCase

from surfactant_example.contributed_ui.surfactant_contributed_ui import (
    SURFACTANT_PLUGIN_ID
)
from surfactant_example.contributed_ui.templates import (
    ExecutionLayerTemplate, IngredientTemplate)
from surfactant_example.data.gromacs_database import GromacsDatabase


class TestExecutionLayerTemplate(TestCase):

    def setUp(self):
        self.gromacs_database = GromacsDatabase()
        self.layer_template = ExecutionLayerTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID,
        )

    def test___init__(self):
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory",
            self.layer_template.id
        )

        self.assertEqual(3, len(self.layer_template.ingredient_templates))
        self.assertEqual(3, self.layer_template.n_ingredients)
        self.assertEqual(
            3, len(self.layer_template.surfactant_template_list)
        )
        self.assertEqual(
            3, len(self.layer_template.secondary_surfactant_list)
        )
        self.assertEqual(
            self.layer_template.surfactant_template_list[0],
            self.layer_template.primary_surfactant_template
        )
        self.assertEqual(
            self.layer_template.empty_surfactant_template,
            self.layer_template.secondary_surfactant_template
        )
        self.assertEqual(
            2,
            len(self.layer_template.primary_surfactant_template
                .ingredient.fragments)
        )
        self.assertIsNone(
            self.layer_template.secondary_surfactant_template.ingredient
        )
        self.assertEqual(
            2, len(self.layer_template.salt_template.ingredient.fragments)
        )
        self.assertEqual(
            1, len(self.layer_template.solvent_template.ingredient.fragments)
        )

    def test_id(self):

        self.layer_template.plugin_id = 'force.bdss.surfactant.plugin.v1'
        new_id = "force.bdss.surfactant.plugin.v1.factory"
        self.assertEqual(new_id, self.layer_template.id)
        self.assertEqual(
            new_id, self.layer_template.primary_surfactant_template.plugin_id
        )
        self.assertEqual(
            new_id, self.layer_template.secondary_surfactant_template.plugin_id
        )
        self.assertEqual(
            new_id, self.layer_template.salt_template.plugin_id
        )
        self.assertEqual(
            new_id, self.layer_template.solvent_template.plugin_id
        )

    def test_secondary_surfactant_list(self):

        dpc_template = self.layer_template.secondary_surfactant_list[-1]

        self.layer_template.secondary_surfactant_template = (
            dpc_template
        )
        self.assertEqual(4, self.layer_template.n_ingredients)

        self.layer_template.primary_surfactant_template = (
            dpc_template
        )
        self.assertNotIn(
            dpc_template,
            self.layer_template.secondary_surfactant_list
        )
        self.assertEqual(
            self.layer_template.empty_surfactant_template,
            self.layer_template.secondary_surfactant_template
        )
        self.assertEqual(3, self.layer_template.n_ingredients)

    def test_create_database_templates(self):

        templates = self.layer_template.create_database_templates()
        self.assertEqual(3, len(templates))

        names = ['Sodium Dodecyl Sulfate',
                 'Sodium Chloride',
                 'Water']
        input_slots = [[], [], []]
        output_slots = [[{'name': 'sodium_dodecyl_sulfate_ingredient'}],
                        [{'name': 'sodium_chloride_ingredient'}],
                        [{'name': 'water_ingredient'}]]

        for index, template in enumerate(templates):
            keys = list(template.keys())
            self.assertListEqual(
                ['id', 'model_data'], keys
            )
            self.assertEqual(
                "force.bdss.surfactant.plugin.example.v0.factory.database",
                template['id']
            )
            self.assertEqual(
                'Model', template['model_data']['input_mode']
            )
            self.assertEqual(
                names[index], template['model_data']['name']
            )
            self.assertEqual(
                input_slots[index],
                template['model_data']['input_slot_info']
            )
            self.assertEqual(
                output_slots[index],
                template['model_data']['output_slot_info']
            )

    def test_create_formulation_template(self):

        template = self.layer_template.create_formulation_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.formulation",
            template['id']
        )
        self.assertEqual(
            {
                "n_surfactants": 1,
                "input_slot_info": [
                    {"name": "sodium_dodecyl_sulfate_ingredient"},
                    {"name": "sodium_dodecyl_sulfate_conc"},
                    {"name": "sodium_chloride_ingredient"},
                    {"name": "sodium_chloride_conc"},
                    {"name": "water_ingredient"}
                ],
                "output_slot_info": [{"name": "formulation"}]
            },
            template['model_data']
        )

    def test_create_simulation_template(self):

        template = self.layer_template.create_simulation_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.simulation",
            template['id']
        )
        self.assertEqual(
            {
                "name": "surfactant_experiment",
                "size": 500,
                "dry_run": False,
                "input_slot_info": [{"name": "formulation"}],
                "output_slot_info": [{"name": "results"}]
            },
            template['model_data']
        )

    def test_create_viscosity_template(self):

        template = self.layer_template.create_viscosity_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.viscosity",
            template['id']
        )
        self.assertEqual(
            {
                "input_slot_info": [{"name": "results"}],
                "output_slot_info": [{"name": "viscosity"}]
            },
            template['model_data']
        )

    def test_create_micelle_template(self):

        template = self.layer_template.create_micelle_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.micelle",
            template['id']
        )
        self.assertEqual(
            {
                'method': 'atomic',
                "fragment_symbols": ['SDS'],
                "r_thresh": 0.98,
                "input_slot_info": [{'name': 'formulation'},
                                    {"name": "results"}],
                "output_slot_info": [{"name": "micelle"}]
            },
            template['model_data']
        )

        dpc_template = self.layer_template.secondary_surfactant_list[1]
        self.layer_template.secondary_surfactant_template = (
            dpc_template
        )

        template = self.layer_template.create_micelle_template()

        self.assertEqual(
            {
                'method': 'atomic',
                "fragment_symbols": ['SDS', 'DPC'],
                "r_thresh": 0.98,
                "input_slot_info": [{'name': 'formulation'},
                                    {"name": "results"}],
                "output_slot_info": [{"name": "micelle"}]
            },
            template['model_data']
        )

    def test_create_cost_template(self):

        template = self.layer_template.create_cost_template()

        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.cost",
            template['id']
        )
        self.assertEqual(
            {
                "input_slot_info": [{"name": "formulation"}],
                "output_slot_info": [{"name": "cost"}]
            },
            template['model_data']
        )

    def test_create_template(self):

        template = self.layer_template.create_template()

        factory_list = [
            ['database', 'database', 'database'],
            ['formulation'],
            ['simulation'],
            ['micelle', 'cost']
        ]

        self.assertEqual(len(factory_list), len(template))

        for factories, layer_template in zip(factory_list, template):
            self.assertEqual(
                len(factories), len(layer_template['data_sources']))
            for index, factory in enumerate(factories):
                keys = list(layer_template['data_sources'][index].keys())
                self.assertListEqual(
                    ['id', 'model_data'], keys
                )

    def test_create_template_secondary_surfactant(self):

        ingredient_names = [
            'Dodecyl Phosphocholine',
            'Sodium Laureth Sulfate']
        variable_names = [
            'dodecyl_phosphocholine',
            'sodium_laureth_sulfate']

        for ingredient_name, variable_name in zip(
                ingredient_names, variable_names):

            ingredient = self.gromacs_database.get_ingredient(
                ingredient_name)
            ingredient_template = IngredientTemplate(
                plugin_id=self.layer_template.id,
                ingredient=ingredient)
            self.layer_template.surfactant_template_list.append(
                ingredient_template)
            self.layer_template.secondary_surfactant_template = (
                self.layer_template.surfactant_template_list[-1]
            )

            self.assertEqual(4, self.layer_template.n_ingredients)
            template = self.layer_template.create_template()

            first_layer_ds = template[0]['data_sources']
            second_layer_ds = template[1]['data_sources']

            self.assertEqual(4, len(first_layer_ds))
            self.assertEqual(
                [{"name": f"{variable_name}_ingredient"}],
                first_layer_ds[1]['model_data']['output_slot_info'])

            self.assertEqual(1, len(second_layer_ds))
            self.assertIn(
                {"name": f"{variable_name}_ingredient"},
                second_layer_ds[0]['model_data']['input_slot_info'])
            self.assertIn(
                {"name": f"{variable_name}_conc"},
                second_layer_ds[0]['model_data']['input_slot_info'])
