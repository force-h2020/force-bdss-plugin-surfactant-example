from force_bdss.api import Slot
from force_gromacs.data_sources import SimulationDataSource

from .surfactant_simulation_builder import (
    SurfactantSimulationBuilder
)


class SurfactantSimulationDataSource(SimulationDataSource):
    """Subclass of force_gromacs `SimulationDataSource` class with
    a defined `create_simulation_builder` method that sets up a Gromacs
    simulation specific to the surfactant formulation use case."""

    def create_simulation_builder(self, model, parameters):

        formulation = parameters[0].value

        # Create unique simulation name based on surfactant and
        # salt concentration
        experiment_name = '_'.join([model.name, formulation.ref])

        # Generate `GromacsSimulationBuilder` object for a surfactant
        # simulation simulation
        simulation = SurfactantSimulationBuilder(
            name=experiment_name,
            directory=model.output_directory,
            size=model.size,
            n_steps=model.n_steps,
            martini_parameters=model.martini_parameters,
            minimize_parameters=model.md_min_parameters,
            production_parameters=model.md_prod_parameters,
            mpi_run=model.mpi_run,
            n_proc=model.n_proc,
            dry_run=model.dry_run,
            formulation=formulation
        )

        return simulation

    def slots(self, model):
        """Overloads method on parent class to provide Ingredient
        objects as input slots"""

        _, output_slots = super(
            SurfactantSimulationDataSource, self).slots(model)

        input_slots = (
            Slot(
                description=f"Chemical formulation data",
                type="FORMULATION"),
        )

        return (
            input_slots,
            output_slots
        )
