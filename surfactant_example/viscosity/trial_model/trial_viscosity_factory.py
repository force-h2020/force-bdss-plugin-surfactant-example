from force_bdss.api import BaseDataSourceFactory

from .trial_viscosity_data_source import TrialViscosityDataSource
from .trial_viscosity_model import TrialViscosityDataSourceModel


class TrialViscosityFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "trial_viscosity"

    def get_name(self):
        return "Trial Viscosity"

    def get_model_class(self):
        return TrialViscosityDataSourceModel

    def get_data_source_class(self):
        return TrialViscosityDataSource
