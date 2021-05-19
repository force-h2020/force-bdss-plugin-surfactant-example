from traits.api import (
    Instance, Unicode, Property, Int, List, cached_property,
    on_trait_change
)
from traitsui.api import (
    View, HGroup, Group, Item, Heading, InstanceEditor
)

from surfactant_example.data.gromacs_database import GromacsDatabase

from .base_template import BaseTemplate
from .ingredient_template import IngredientTemplate


class ExecutionLayerTemplate(BaseTemplate):

    # ------------------
    # Regular Attributes
    # ------------------

    #: Template referring to the primary surfactant data
    primary_surfactant_template = Instance(IngredientTemplate)

    #: Template referring to the secondary surfactant data
    secondary_surfactant_template = Instance(IngredientTemplate)

    #: A list of possible surfactant ingredient to choose from
    surfactant_template_list = List(IngredientTemplate)

    #: An empty surfactant Template
    empty_surfactant_template = Instance(IngredientTemplate)

    #: Template referring to the chloride ion data
    salt_template = Instance(IngredientTemplate)

    #: Template referring to the solvent data
    solvent_template = Instance(IngredientTemplate)

    #: Internal database of available Ingredient objects
    _gromacs_database = Instance(GromacsDatabase)

    # ------------------
    #     Properties
    # ------------------

    #: Factory ID for Workflow
    id = Property(Unicode, depends_on='plugin_id')

    #: List containing all fragment templates to be used in
    #: a generated Workflow
    ingredient_templates = Property(
        List(IngredientTemplate),
        depends_on='primary_surfactant_template,'
                   'secondary_surfactant_template'
    )

    #: Number of Ingredients
    n_ingredients = Property(
        Int, depends_on='ingredient_templates[]'
    )

    # ------------------
    #     Properties
    # ------------------

    #: A list of possible secondary surfactant ingredient, including an
    #: empty ingredient option
    secondary_surfactant_list = Property(
        List(IngredientTemplate),
        depends_on='surfactant_template_list,'
                   'primary_surfactant_template')

    # ------------------
    #        View
    # ------------------

    traits_view = View(
        HGroup(
            Group(
                Heading("Primary Surfactant"),
                Item("primary_surfactant_template",
                     editor=InstanceEditor(
                         name='surfactant_template_list'
                     ),
                     style='custom'),
                show_labels=False
            ),
            Group(
                Heading("Secondary Surfactant"),
                Item("secondary_surfactant_template",
                     editor=InstanceEditor(
                         name='secondary_surfactant_list'
                     ),
                     style='custom'),
                show_labels=False
            )
        )
    )

    # ------------------
    #      Defaults
    # ------------------

    def _empty_surfactant_template_default(self):
        return IngredientTemplate(
            plugin_id=self.id
        )

    def __gromacs_database_default(self):
        return GromacsDatabase()

    def _surfactant_template_list_default(self):

        surfactants = self._gromacs_database.get_role(
            'Surfactant')

        surfactant_templates = [
            IngredientTemplate(
                plugin_id=self.id,
                ingredient=surfactant)
            for surfactant in surfactants]

        return surfactant_templates

    def _primary_surfactant_template_default(self):
        return self.surfactant_template_list[0]

    def _secondary_surfactant_template_default(self):
        return self.empty_surfactant_template

    def _salt_template_default(self):

        salt = self._gromacs_database.get_ingredient(
            'Sodium Chloride')

        return IngredientTemplate(
            plugin_id=self.id,
            ingredient=salt
        )

    def _solvent_template_default(self):

        water = self._gromacs_database.get_ingredient(
            'Water')

        return IngredientTemplate(
            plugin_id=self.id,
            ingredient=water
        )

    # ------------------
    #      Listeners
    # ------------------

    def _get_id(self):
        return '.'.join([self.plugin_id, "factory"])

    @cached_property
    def _get_ingredient_templates(self):
        templates = [self.primary_surfactant_template,
                     self.salt_template,
                     self.solvent_template]

        if self.secondary_surfactant_template.ingredient:
            templates.insert(
                1, self.secondary_surfactant_template)

        return templates

    @cached_property
    def _get_n_ingredients(self):
        return len(self.ingredient_templates)

    @cached_property
    def _get_secondary_surfactant_list(self):

        secondary_list = [self.empty_surfactant_template]
        secondary_list += [
            surfactant for surfactant in self.surfactant_template_list
            if surfactant != self.primary_surfactant_template
        ]

        return secondary_list

    @on_trait_change('primary_surfactant_template')
    def update_secondary_surfactant_template(self):
        if (self.primary_surfactant_template
                == self.secondary_surfactant_template):
            self.secondary_surfactant_template = (
                    self._secondary_surfactant_template_default()
            )

    @on_trait_change('plugin_id')
    def update_plugin_id(self):
        for surfactant_template in self.surfactant_template_list:
            surfactant_template.plugin_id = self.id
        self.empty_surfactant_template.plugin_id = self.id
        self.salt_template.plugin_id = self.id
        self.solvent_template.plugin_id = self.id

    # ------------------
    #   Public Methods
    # ------------------

    def create_database_templates(self):

        templates = []

        for ingredient_template in self.ingredient_templates:
            template = ingredient_template.create_template()
            templates.append(template)

        return templates

    def create_formulation_template(self):

        input_slot_info = []

        for template in self.ingredient_templates:
            if template.ingredient.role != 'Solvent':
                input_slot_info.append(
                    {"name": f"{template.variable_name}_ingredient"})
                input_slot_info.append(
                    {"name": f"{template.variable_name}_conc"})
            else:
                input_slot_info.append(
                    {"name": f"{template.variable_name}_ingredient"})

        return {
            "id": f"{self.id}.formulation",
            "model_data": {
                "n_surfactants": self.n_ingredients - 2,
                "input_slot_info": input_slot_info,
                "output_slot_info": [{"name": "formulation"}]
            }
        }

    def create_simulation_template(self):

        return {
            "id": f"{self.id}.simulation",
            "model_data": {
                "name": "surfactant_experiment",
                "size": 500,
                "dry_run": False,
                "input_slot_info": [{"name": "formulation"}],
                "output_slot_info": [{"name": "results"}]
            }
        }

    def create_micelle_template(self):

        surfactants = [
            template.ingredient for template in self.ingredient_templates
            if template.ingredient.role == 'Surfactant'
        ]

        fragment_symbols = [
            surfactant.fragments[0].symbol for surfactant in surfactants
        ]

        return {
            "id": f"{self.id}.micelle",
            "model_data": {
                "method": 'atomic',
                "fragment_symbols": fragment_symbols,
                "r_thresh": 0.98,
                "input_slot_info": [{"name": "formulation"},
                                    {"name": "results"}],
                "output_slot_info": [{"name": "micelle"}]
            }
        }

    def create_viscosity_template(self):
        return {
            "id": f"{self.id}.viscosity",
            "model_data": {
                "input_slot_info": [{"name": "results"}],
                "output_slot_info": [{"name": "viscosity"}]
            }
        }

    def create_cost_template(self):
        return {
            "id": f"{self.id}.cost",
            "model_data": {
                "input_slot_info": [{"name": "formulation"}],
                "output_slot_info": [{"name": "cost"}]
            }
        }

    def create_template(self):
        return [
            {'data_sources': self.create_database_templates()},
            {'data_sources': [self.create_formulation_template()]},
            {'data_sources': [self.create_simulation_template()]},
            {
                'data_sources': [
                    self.create_micelle_template(),
                    self.create_cost_template()
                ]
            }
        ]
