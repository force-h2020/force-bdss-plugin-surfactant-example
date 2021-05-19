from traitsui.api import View, Item

from force_bdss.api import (
    CategoricalMCOParameterFactory,
    CategoricalMCOParameter,
)


class IngredientMCOParameter(CategoricalMCOParameter):
    def default_traits_view(self):
        return View(Item("categories", label="Ingredients"))


class IngredientMCOParameterFactory(CategoricalMCOParameterFactory):
    """The factory of the above model"""

    def get_identifier(self):
        return "ingredient"

    #: A name that will appear in the UI to identify this parameter.
    def get_name(self):
        return "Ingredient Parameter"

    #: Definition of the associated model class.
    def get_model_class(self):
        return IngredientMCOParameter

    #: A long description of the parameter
    def get_description(self):
        return "A categorical parameter defining a chemical ingredient."
