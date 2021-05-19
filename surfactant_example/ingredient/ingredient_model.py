from traits.api import Float, Enum, Unicode
from traitsui.api import View, Item

from force_gromacs.data_sources import MoleculeDataSourceModel

from surfactant_example.mco.driver_events import IngredientProgressEvent


class IngredientDataSourceModel(MoleculeDataSourceModel):
    """Class containing all parameters for a chemical ingredient."""

    #: Name of ingredient in formulation
    name = Unicode()

    #: Role of ingredient in formulation
    role = Enum('Surfactant', 'Salt', 'Solvent',
                desc='Role of ingredient in simulation',
                changes_slots=True)

    #: Price of ingredient in $USD / kg
    price = Float(0.0,
                  desc='Price of fragment ingredient in $USD / kg')

    def default_traits_view(self):
        """Specifies view for model, combining attributes of
        this class and MoleculeDataSourceModel"""
        traits_view = View(
            Item("name"),
            Item("role"),
            Item("price"),
            Item('n_fragments'),
            Item('fragment_numbers')
        )

        return traits_view

    def notify_ingredient(self, ingredient):
        """Notify a CSVWriter of the ingredient. Assigns a
        `IngredientProgressEvent` to the `event` attribute.
        By doing so it can be picked up by the `Workflow` and
        passed onto any `NotificationListeners` present.

        Parameters
        ----------
        ingredient: Ingredient
            Ingredient object to pass on to CSVWriter
        """

        self.notify(
            IngredientProgressEvent(
                name=ingredient.name, role=ingredient.role
            )
        )
