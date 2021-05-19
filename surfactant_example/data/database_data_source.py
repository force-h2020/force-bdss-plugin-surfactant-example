from force_bdss.api import BaseDataSource, DataValue, Slot

from .gromacs_database import GromacsDatabase


class DatabaseDataSource(BaseDataSource):
    """Class that returns an Ingredient object from
    a query on a provided database"""

    _gromacs_database = GromacsDatabase()

    def run(self, model, parameters):

        if model.input_mode == 'Parameter':
            key = parameters[0].value
        else:
            key = model.name

        ingredient = self._gromacs_database.get_ingredient(key)

        return [
                DataValue(type="INGREDIENT", value=ingredient)
            ]

    def slots(self, model):

        input_slots = tuple()
        if model.input_mode == 'Parameter':
            input_slots += (Slot(
                description=f"Ingredient name",
                type="NAME"),)

        return (
            input_slots,
            (
                Slot(description=f"Ingredient data",
                     type="INGREDIENT"),
            )
        )
