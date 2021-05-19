from surfactant_example.ingredient import Ingredient

from .probe_fragments import (
    ProbePrimarySurfactant, ProbePositiveIon, ProbeSecondarySurfactant,
    ProbeNegativeIon, ProbeSolvent
)


class ProbePrimaryIngredient(Ingredient):

    def __init__(self, price=100):

        super(ProbePrimaryIngredient, self).__init__(
            fragments=[ProbePrimarySurfactant(),
                       ProbePositiveIon()],
            price=price,
            role='Surfactant'
        )


class ProbeSecondaryIngredient(Ingredient):

    def __init__(self, price=200):

        super(ProbeSecondaryIngredient, self).__init__(
            fragments=[ProbeSecondarySurfactant()],
            price=price,
            role='Surfactant'
        )


class ProbeSaltIngredient(Ingredient):

    def __init__(self, price=1):

        super(ProbeSaltIngredient, self).__init__(
            fragments=[ProbePositiveIon(),
                       ProbeNegativeIon()],
            price=price,
            role='Salt'
        )


class ProbeSolventIngredient(Ingredient):

    def __init__(self, price=0.5):

        super(ProbeSolventIngredient, self).__init__(
            fragments=[ProbeSolvent()],
            price=price,
            role='Solvent'
        )
