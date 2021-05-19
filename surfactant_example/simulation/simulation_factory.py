from force_bdss.api import BaseDataSourceFactory

from .simulation_data_source import SurfactantSimulationDataSource
from .simulation_model import SimulationModel


class SimulationFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "simulation"

    def get_name(self):
        return "Gromacs Simulation"

    def get_model_class(self):
        return SimulationModel

    def get_data_source_class(self):
        return SurfactantSimulationDataSource
