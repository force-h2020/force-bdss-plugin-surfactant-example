from traits.api import (
    Unicode, Property, Instance, cached_property)
from traitsui.api import View, Item, InstanceEditor, Group

from surfactant_example.ingredient import Ingredient
from surfactant_example.utilities import process_variable_name

from .base_template import BaseTemplate


class IngredientTemplate(BaseTemplate):
    """BaseTemplate subclass to generate chemical Ingredient options
    for SurfactantContributedUI"""

    # --------------------
    #  Required Attributes
    # --------------------

    #: Simulation experiment Ingredient
    ingredient = Instance(Ingredient)

    # ------------------
    #     Properties
    # ------------------

    #: Factory ID for Workflow
    id = Property(Unicode, depends_on='plugin_id')

    #: Human readable name of chemical Ingredient
    name = Property(Unicode, depends_on='ingredient.name')

    #: Variable of Ingredient
    variable_name = Property(
        Unicode, depends_on='ingredient.name')

    # ------------------
    #       View
    # ------------------

    traits_view = View(
        Group(
            Item("ingredient",
                 style='custom',
                 editor=InstanceEditor()
                 ),
            show_labels=False
        )
    )

    # ------------------
    #     Listeners
    # ------------------

    def _get_id(self):
        return '.'.join([self.plugin_id, "database"])

    def _get_name(self):
        if self.ingredient:
            return self.ingredient.name
        return 'None'

    @cached_property
    def _get_variable_name(self):
        if self.ingredient:
            variable_name = f"{self.ingredient.name}".lower()
            variable_name = process_variable_name(variable_name)
            return variable_name
        return ''

    # ------------------
    #   Public Methods
    # ------------------

    def create_database_template(self):
        """Creates template workflow object for a DatabaseDataSource
        object that that loads an Ingredient from a GromacsDatabase"""

        template = {
            "id": self.id,
            "model_data": {
                'input_mode': 'Model',
                "name": self.ingredient.name,
                "input_slot_info": [],
                "output_slot_info": [
                    {"name": f"{self.variable_name}_ingredient"}
                ]
            }
        }

        return template

    def create_template(self):
        if self.ingredient:
            return self.create_database_template()
        return {}
