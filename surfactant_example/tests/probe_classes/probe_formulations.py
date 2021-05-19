from surfactant_example.formulation.formulation import Formulation

from .probe_ingredients import (
    ProbeSolventIngredient, ProbeSaltIngredient, ProbePrimaryIngredient,
    ProbeSecondaryIngredient)


class ProbeFormulation(Formulation):

    def __init__(self):

        ingredients = [ProbePrimaryIngredient(),
                       ProbeSecondaryIngredient(),
                       ProbeSaltIngredient(),
                       ProbeSolventIngredient()]
        concentrations = [12, 4, 0.5, 83.5]

        super(ProbeFormulation, self).__init__(
            ingredients=ingredients,
            concentrations=concentrations
        )
