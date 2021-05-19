import numpy as np

from force_bdss.api import BaseDataSource, DataValue, Slot

from .formulation import Formulation


class MissingIngredientException(Exception):
    """Raised if a Formulation does not contain the appropriate
    Ingredients.
    """


class FormulationDataSource(BaseDataSource):
    """Class that generates a Formulation object containg surfactants
    from a list of Ingredient objects and their respective
    concentrations"""

    # Ingredient roles required by the surfactant Formulation
    _roles_required = ['Surfactant', 'Salt', 'Solvent']

    def _check_ingredient_roles(self, ingredients):
        """Ensure incoming Ingredients meet role requirements for
        Formulation"""
        for role in self._roles_required:
            present = [
                ingredient for ingredient in ingredients
                if ingredient.role == role
            ]

            if not present:
                raise MissingIngredientException(
                    f"No Ingredients of type '{role}' defined"
                )

        return True

    def run(self, model, parameters):

        ingredients = []
        concentrations = []

        for parameter in parameters:
            if parameter.type == 'INGREDIENT':
                ingredients.append(parameter.value)
            elif parameter.type == 'CONCENTRATION':
                concentrations.append(parameter.value)

        # Check formulation composition
        self._check_ingredient_roles(ingredients)

        # Calculate missing solvent concentration (in excess)
        solvent_conc = calculate_solvent_conc(concentrations)
        concentrations.append(solvent_conc)

        formulation = Formulation(
            ingredients=ingredients,
            concentrations=concentrations
        )

        return [
            DataValue(value=formulation, type='FORMULATION')
        ]

    def slots(self, model):

        input_slots = tuple()

        for index in range(model.n_surfactants):
            input_slots += (
                Slot(description=f"Surfactant {index + 1} data",
                     type="INGREDIENT"),
                Slot(description=f"Surfactant {index + 1} concentration",
                     type="CONCENTRATION"))

        input_slots += (
            Slot(description=f"Salt data", type="INGREDIENT"),
            Slot(description=f"Salt concentration", type="CONCENTRATION"),
            Slot(description=f"Solvent data", type="INGREDIENT")
        )

        return (
            input_slots,
            (
                Slot(description=f"Chemical formulation",
                     type="FORMULATION"),
            )
        )


def calculate_solvent_conc(concentrations):
    """Calculate solvent concentration from concentrations of other
    ingredients"""

    solvent_conc = 100 - np.sum(concentrations)

    assert 0 < solvent_conc < 100, (
        'Solvent concentration must be between '
        '0-100 % by weight: check input concentration'
        ' parameter values'
    )

    return solvent_conc
