from unittest import TestCase

from surfactant_example.contributed_ui.surfactant_contributed_ui import (
    SURFACTANT_PLUGIN_ID
)
from surfactant_example.contributed_ui.templates\
    .ingredient_template import IngredientTemplate
from surfactant_example.data.gromacs_database import GromacsDatabase


class TestIngredientTemplate(TestCase):

    def setUp(self):
        self.gromacs_database = GromacsDatabase()

        sds = self.gromacs_database.get_ingredient(
            'Sodium Dodecyl Sulfate')
        self.ingredient_template = IngredientTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID + '.factory',
            ingredient=sds
        )

        water = self.gromacs_database.get_ingredient('Water')
        self.water_fragment = water.fragments[0]

    def test___init__(self):
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.database",
            self.ingredient_template.id
        )
        self.assertEqual(
            100, self.ingredient_template.ingredient.price
        )
        self.assertEqual(
            'Sodium Dodecyl Sulfate',
            self.ingredient_template.ingredient.name
        )
        self.assertEqual(
            'sodium_dodecyl_sulfate',
            self.ingredient_template.variable_name
        )

    def test_id(self):
        self.ingredient_template.plugin_id = (
            'force.bdss.surfactant.plugin.v1.factory'
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.v1.factory.database",
            self.ingredient_template.id
        )

    def test_variable_name(self):

        self.ingredient_template.ingredient.name = "Surfactant #1"

        self.assertEqual(
            'surfactant_1',
            self.ingredient_template.variable_name
        )

    def test_create_template(self):
        template = self.ingredient_template.create_template()
        keys = list(template.keys())
        self.assertListEqual(
            ['id', 'model_data'], keys
        )
        self.assertEqual(
            "force.bdss.surfactant.plugin.example.v0.factory.database",
            template['id']
        )

        keys = list(template['model_data'].keys())
        self.assertListEqual(
            ["input_mode", "name",
             "input_slot_info", "output_slot_info"],
            keys
        )

        self.assertEqual('Model', template['model_data']['input_mode'])
        self.assertEqual('Sodium Dodecyl Sulfate',
                         template['model_data']['name'])
        self.assertEqual([], template['model_data']["input_slot_info"])
        self.assertEqual(
            [{"name": "sodium_dodecyl_sulfate_ingredient"}],
            template['model_data']["output_slot_info"]
        )
