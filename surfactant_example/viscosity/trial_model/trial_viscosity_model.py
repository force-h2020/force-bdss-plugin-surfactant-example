from traits.api import (
    List, Unicode, Float, HasTraits, Enum, Int, Button)
from traitsui.api import (
    View, Item, TableEditor, ObjectColumn, HGroup)

from force_bdss.api import BaseDataSourceModel
from force_bdss.core.base_model import pop_dunder_recursive


class ViscosityModelParameters(HasTraits):
    """Parameters for a simplified model predicting viscosity
    contributions from each Ingredient"""

    # Name of the Ingredient
    name = Unicode()

    # Mean of Gaussian, determines concentration value for
    # maximum viscosity contribution
    mean = Float()

    # Standard deviation of Gaussian, determines maximum and
    # spread of viscosity contributions
    sigma = Float()

    traits_view = View(
        Item("name"),
        Item("mean"),
        Item("sigma"),
        title='Add Ingredient Viscosity Parameters',
        buttons=['OK', 'Cancel']
    )

    def __getstate__(self):
        state = pop_dunder_recursive(super().__getstate__())
        return state


class TrialViscosityDataSourceModel(BaseDataSourceModel):
    """UI input for trial viscosity model parameters. Each Ingredient
    is assigned a mean and sigma parameter for a Gaussian function
    that determines its contribution to the Formulation viscosity"""

    # List containing names of each ingredient with their
    # respective model parameters
    ingredient_models = List(
        ViscosityModelParameters,
        desc='Values corresponding to viscosity calculations'
             'for each ingredient')

    # How to include viscosity contributions from each Ingredient,
    # either as a Summation or a Product
    calculation_mode = Enum('Sum', 'Product')

    # UI selected ViscosityModelParameters objects, used as a
    # reference for editing / deleting items from the UI table
    selected_table_index = Int(transient=True)

    # Buttons used to add or removed UI table items, referrring to
    # elements in ingredient_models
    add_viscosity_model_button = Button('Add Row')
    remove_viscosity_model_button = Button('Delete Row')

    def default_traits_view(self):

        table_editor = TableEditor(
            columns=[ObjectColumn(name='name'),
                     ObjectColumn(name='mean'),
                     ObjectColumn(name='sigma')],
            selected_indices='selected_table_index',
            show_toolbar=True,
            editable=True,
            deletable=True,
            sortable=False,
            row_factory=ViscosityModelParameters
        )

        return View(
            Item("calculation_mode"),
            Item("ingredient_models",
                 editor=table_editor,
                 style='custom'),
            HGroup(
                Item("add_viscosity_model_button"),
                Item("remove_viscosity_model_button"),
                show_labels=False
            )
        )

    def __init__(self, *args, **kwargs):

        # NOTE: this is a work around, since the WorkflowReader
        # and WorkflowWriter classes in force_bdss dont know how to
        # serialise ViscosityModelParameters classes.
        ingredient_models = kwargs.pop("ingredient_models", None)

        super(TrialViscosityDataSourceModel, self).__init__(
            *args, **kwargs)

        if ingredient_models is not None:
            self.ingredient_models = [
                ViscosityModelParameters(**kwargs)
                for kwargs in ingredient_models
            ]

    def _selected_table_index_default(self):
        """Selects last element in ingredient_models list"""
        return len(self.ingredient_models) - 1

    def _add_viscosity_model_button_fired(self):
        """Add a new element to the ingredient_models attribute"""
        self.ingredient_models.append(ViscosityModelParameters())
        self.selected_table_index = (
            self._selected_table_index_default())

    def _remove_viscosity_model_button_fired(self):
        """Remove UI selected element from the ingredient_models
        attribute"""
        if self.ingredient_models:
            self.ingredient_models.pop(
                self.selected_table_index)

        # Ensures index does not reference non-existent elements
        if self.selected_table_index >= len(self.ingredient_models):
            self.selected_table_index = (
                self._selected_table_index_default())
