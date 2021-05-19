from force_bdss.api import BaseDataSourceFactory

from .viscosity_model import ViscosityDataSourceModel
from .viscosity_data_source import ViscosityDataSource


class ViscosityFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "viscosity"

    def get_name(self):
        return "Viscosity Calculator"

    def get_model_class(self):
        return ViscosityDataSourceModel

    def get_data_source_class(self):
        return ViscosityDataSource
