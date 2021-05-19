import os
from force_gromacs.data_sources.simulation.simulation_model import (
    SimulationDataSourceModel)

from surfactant_example.data.gromacs_files.path import get_file


class SimulationModel(SimulationDataSourceModel):

    def _martini_parameters_default(self):
        return get_file(os.path.join('topologies', 'martini_v2.2.itp'))

    def _md_min_parameters_default(self):
        return get_file(os.path.join('md_parameters', 'minimize.mdp'))

    def _md_prod_parameters_default(self):
        return get_file(os.path.join('md_parameters', 'production.mdp'))
