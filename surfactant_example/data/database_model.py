from traits.api import Enum, Unicode
from traitsui.api import View, Item

from force_bdss.api import BaseDataSourceModel


class DatabaseModel(BaseDataSourceModel):

    input_mode = Enum('Parameter', 'Model', changes_slots=True)

    name = Unicode()

    traits_view = View(
        Item('input_mode'),
        Item('name', visible_when="input_mode=='Model'")
    )
