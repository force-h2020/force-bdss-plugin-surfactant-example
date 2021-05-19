from traits.api import (
    on_trait_change, Instance
)
from traitsui.api import (
    Group, Heading, Item, InstanceEditor
)

from force_bdss.api import plugin_id
from force_wfmanager.ui import ContributedUI

from .templates import (
    MCOTemplate, ExecutionLayerTemplate,
    NotificationListenerTemplate
)

_GROMACS_PLUGIN_ID = plugin_id("gromacs", "wrapper", 0)
SURFACTANT_PLUGIN_ID = plugin_id("surfactant", "example", 0)


class SurfactantContributedUI(ContributedUI):
    """A simplified UI for the surfactant formulation user case, allowing
    for selection of fragment ingredient and concentrations for a
    set of Gromacs experiments"""

    # ------------------
    # Regular Attributes
    # ------------------

    #: Name for the UI in selection screen
    name = "Simplified Surfactant Workflow"

    #: Description of the UI
    desc = (
        "A simplified UI which allows the selection concentration"
        " ranges for a set of pre-defined chemicals"
    )

    #: The Template that generates MCO components of the Workflow
    mco_template = Instance(MCOTemplate)

    #: The Template that generates ExecutionLayer components of the
    #: Workflow
    execution_layers_template = Instance(ExecutionLayerTemplate)

    #: The Template that generates NotificationListener components of the
    #: Workflow
    notification_listener_template = Instance(NotificationListenerTemplate)

    def __init__(self, *args, **kwargs):
        super(SurfactantContributedUI, self).__init__(*args, **kwargs)
        self.workflow_data_update()

    # ------------------
    #      Defaults
    # ------------------

    def _workflow_data_default(self):
        return {"version": "1.1",
                "workflow": {
                    'mco_model': {},
                    'execution_layers': [],
                    "notification_listeners": []}
                }

    def _mco_template_default(self):
        return MCOTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID
        )

    def _execution_layers_template_default(self):
        return ExecutionLayerTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID
        )

    def _notification_listener_template_default(self):
        return NotificationListenerTemplate(
            plugin_id=SURFACTANT_PLUGIN_ID,
            gromacs_plugin_id=_GROMACS_PLUGIN_ID
        )

    def _workflow_group_default(self):
        workflow_group = Group(
            Heading("Chemical Ingredient Settings", springy=True),
            Group(
                Item('execution_layers_template',
                     editor=InstanceEditor(),
                     style='custom'),
                show_labels=False
            ),
            Heading("Concentration Settings", springy=True),
            Group(
                Item('mco_template',
                     editor=InstanceEditor(),
                     style='custom'),
                show_labels=False
            )
        )
        return workflow_group

    # ------------------
    #      Listeners
    # ------------------

    @on_trait_change('execution_layers_template.n_ingredients')
    def update_enable_secondary_surfactant(self):
        if self.execution_layers_template.n_ingredients == 4:
            self.mco_template.enable_secondary_surfactant = True
        else:
            self.mco_template.enable_secondary_surfactant = False

    @on_trait_change('mco_template.parameter_templates'
                     '.[value,levels,lower_bound,upper_bound,n_samples],'
                     'execution_layers_template.ingredient_templates,'
                     'notification_listener_template')
    def workflow_data_update(self):
        self.update_mco_parameter_names()
        wf_data = {
            "version": "1.1",
            "workflow": {
                "mco_model": self.mco_template.create_template(),
                "execution_layers":
                    self.execution_layers_template.create_template(),
                "notification_listeners":
                    self.notification_listener_template.create_template()
            }
        }
        self.workflow_data = wf_data

    def update_mco_parameter_names(self):

        self.mco_template.primary_surfactant_conc.name = (
            self.execution_layers_template.primary_surfactant_template
                .variable_name
        )
        self.mco_template.secondary_surfactant_conc.name = (
            self.execution_layers_template.secondary_surfactant_template
                .variable_name
        )
        self.mco_template.salt_conc.name = (
            self.execution_layers_template.salt_template
                .variable_name
        )
