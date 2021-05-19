from force_bdss.api import BaseDataSourceFactory

from .micelle_model import MicelleDataSourceModel
from .micelle_data_source import MicelleDataSource


class MicelleFactory(BaseDataSourceFactory):

    def get_identifier(self):
        return "micelle"

    def get_name(self):
        return "Micelle Aggregation Calculator"

    def get_model_class(self):
        return MicelleDataSourceModel

    def get_data_source_class(self):
        return MicelleDataSource
