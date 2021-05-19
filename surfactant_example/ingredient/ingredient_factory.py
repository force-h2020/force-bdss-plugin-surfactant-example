from force_bdss.api import BaseDataSourceFactory

from .ingredient_model import IngredientDataSourceModel
from .ingredient_data_source import IngredientDataSource


class IngredientFactory(BaseDataSourceFactory):
    def get_identifier(self):
        return "ingredient"

    def get_name(self):
        return "Ingredient (Gromacs Molecule)"

    def get_model_class(self):
        return IngredientDataSourceModel

    def get_data_source_class(self):
        return IngredientDataSource
