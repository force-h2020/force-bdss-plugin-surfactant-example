from force_bdss.api import plugin_id
from force_bdss.core_plugins.service_offer_plugin import (
    ServiceOfferExtensionPlugin,
)

from .cost.cost_factory import CostFactory
from .csv_writer.surfactant_csv_writer import SurfactantCSVWriterFactory
from .data.database_factory import DatabaseFactory
from .formulation.formulation_factory import FormulationFactory
from .ingredient.ingredient_factory import IngredientFactory
from .mco.mco_factory import MCOFactory

from .micelle.micelle_factory import MicelleFactory
from .simulation.simulation_factory import SimulationFactory
from surfactant_example.viscosity.trial_model.trial_viscosity_factory import (
    TrialViscosityFactory,
)
from .viscosity.viscosity_factory import ViscosityFactory


PLUGIN_VERSION = 0


class SurfactantPlugin(ServiceOfferExtensionPlugin):
    """This is an example plugin to demonstrate surfactant formulation
    use case for the BDSS.
    """

    id = plugin_id("surfactant", "example", PLUGIN_VERSION)

    def get_name(self):
        return "Surfactant Example"

    def get_description(self):
        return (
            "An example plugin to perform a series "
            "of molecular simulations that evaluate viscosities of "
            "surfactants"
        )

    def get_version(self):
        return PLUGIN_VERSION

    def get_factory_classes(self):
        factory_classes = [
            MCOFactory,
            IngredientFactory,
            SimulationFactory,
            ViscosityFactory,
            MicelleFactory,
            CostFactory,
            SurfactantCSVWriterFactory,
            DatabaseFactory,
            FormulationFactory,
            TrialViscosityFactory,
        ]
        try:
            from .mco.surfactant_nevergrad_mco.ng_mco_factory import (
                SurfactantNevergradMCOFactory)
            factory_classes += [SurfactantNevergradMCOFactory]
        except ImportError:
            pass

        return factory_classes

    def get_contributed_uis(self):
        from .contributed_ui.surfactant_contributed_ui import (
            SurfactantContributedUI,
        )
        return [SurfactantContributedUI]

    def get_service_offer_factories(self):
        from force_wfmanager.ui import IContributedUI

        return [(IContributedUI, self.get_contributed_uis())]

    def get_data_views(self):
        # This import is only needed if data views are ever requested
        from surfactant_example.data_view.formulation_data_view import (
            FormulationDataView)
        return [
            FormulationDataView
        ]
