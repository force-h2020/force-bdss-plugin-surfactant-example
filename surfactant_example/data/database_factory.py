from force_bdss.api import BaseDataSourceFactory

from .database_model import DatabaseModel
from .database_data_source import DatabaseDataSource


class DatabaseFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "database"

    def get_name(self):
        return "Database Ingredient"

    def get_model_class(self):
        return DatabaseModel

    def get_data_source_class(self):
        return DatabaseDataSource
