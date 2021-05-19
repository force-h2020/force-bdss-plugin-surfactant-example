from traits.api import Int

from force_bdss.api import BaseDataSourceModel


class FormulationDataSourceModel(BaseDataSourceModel):
    """Class containing all parameters for a chemical formulation."""

    n_surfactants = Int(
        1,
        desc="Number of surfactant chemical ingredients in formulation",
        changes_slots=True)
