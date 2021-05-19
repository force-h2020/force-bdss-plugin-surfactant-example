from traits.api import (
    Unicode, Enum, Property, Float, Int, ListFloat
)
from traitsui.api import View, Item, ListEditor

from .base_template import BaseTemplate


class ParameterTemplate(BaseTemplate):
    """BaseTemplate subclass to generate MCO Parameter options for
    SurfactantContributedUI"""

    # --------------------
    #  Regular Attributes
    # --------------------

    #: String representing MCOParameter subclass
    parameter_type = Enum('Fixed', 'Ranged', 'Listed')

    #: Name of Parameter
    name = Unicode()

    #: CUBA type of Parameter
    type = Unicode('CONCENTRATION')

    #: MCOParameter level trait
    value = Float(1.0)

    #: RangedMCOParameter lower_bound trait
    lower_bound = Float(0.5)

    #: RangedMCOParameter upper_bound trait
    upper_bound = Float(5.0)

    #: RangedMCOParameter n_samples trait
    n_samples = Int(10)

    #: ListedMCOParameter levels trait
    levels = ListFloat([0.5, 1.0, 3.0])

    # --------------------
    #      Properties
    # --------------------

    #: Factory ID for Workflow
    id = Property(Unicode, depends_on='plugin_id,type')

    # --------------------
    #        View
    # --------------------

    traits_view = View(
        Item('parameter_type'),
        Item("value", visible_when="parameter_type=='Fixed'"),
        Item("lower_bound", visible_when="parameter_type=='Ranged'"),
        Item("upper_bound", visible_when="parameter_type=='Ranged'"),
        Item("n_samples", visible_when="parameter_type=='Ranged'"),
        Item("levels",
             editor=ListEditor(style='simple'),
             visible_when="parameter_type=='Listed'")
    )

    # --------------------
    #      Listeners
    # --------------------

    def _get_id(self):
        return '.'.join([self.plugin_id, 'parameter',
                         self.parameter_type.lower()])

    # --------------------
    #    Public Methods
    # --------------------

    def create_template(self):
        template = {
            "id": self.id,
            "model_data": {
                "name": f"{self.name}_conc",
                "type": self.type
            }
        }

        if self.parameter_type == 'Fixed':
            template['model_data']["value"] = self.value
        elif self.parameter_type == 'Ranged':
            template['model_data']["lower_bound"] = self.lower_bound
            template['model_data']["upper_bound"] = self.upper_bound
            template['model_data']["n_samples"] = self.n_samples
        elif self.parameter_type == 'Listed':
            template['model_data']["levels"] = self.levels

        return template
