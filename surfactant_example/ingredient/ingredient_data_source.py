from force_bdss.api import DataValue, Slot
from force_gromacs.data_sources import MoleculeDataSource

from .ingredient import Ingredient


class IngredientDataSource(MoleculeDataSource):
    """Class that collates and defines all fragment ingredient for a single
    chemical ingredient.
    """

    def run(self, model, parameters):
        """Create an Ingredient object containing n_molecules
        molecular Fragment objects"""

        data_values = super(IngredientDataSource, self).run(model, parameters)

        molecule = data_values[0].value

        ingredient = Ingredient(
            name=model.name,
            role=model.role,
            fragments=molecule.fragments,
            price=model.price,
        )

        assert (
            ingredient.neutral
        ), f"Ingredient {ingredient.name} is not electronically neutral"

        model.notify_ingredient(ingredient)

        return [DataValue(type="INGREDIENT", value=ingredient)]

    def slots(self, model):
        all_slots = super(IngredientDataSource, self).slots(model)

        input_slots = all_slots[0]

        return (
            input_slots,
            (
                Slot(
                    description=f"{model.role} ingredient for a simulation",
                    type="INGREDIENT",
                ),
            ),
        )
