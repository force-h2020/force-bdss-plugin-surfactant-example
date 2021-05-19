from force_bdss.api import (
    FixedMCOParameterFactory,
    ListedMCOParameterFactory,
    RangedMCOParameterFactory
)

from force_nevergrad.mco.ng_mco_factory import NevergradMCOFactory

from surfactant_example.mco.parameters.ingredient import (
    IngredientMCOParameterFactory,
)


class SurfactantNevergradMCOFactory(NevergradMCOFactory):

    def get_identifier(self):
        return "surfactant_nevergrad_mco"

    #: Factory classes of the parameters the MCO supports.
    def get_parameter_factory_classes(self):
        return [
            FixedMCOParameterFactory,
            ListedMCOParameterFactory,
            RangedMCOParameterFactory,
            IngredientMCOParameterFactory,
        ]
