from traits.api import (
    List, Unicode, Property, Instance, Bool, on_trait_change
)
from traitsui.api import (
    View, HGroup, Group, Heading, Item, InstanceEditor
)

from .base_template import BaseTemplate
from .parameter_template import ParameterTemplate


class MCOTemplate(BaseTemplate):
    """BaseTemplate subclass to generate MCO options for
    SurfactantContributedUI"""

    # ------------------
    # Regular Attributes
    # ------------------

    #: Name of the MCO for Workflow plugin id reference
    mco_name = Unicode("surfactant_mco")

    #: Template referring to the primary surfactant concentration
    primary_surfactant_conc = Instance(ParameterTemplate)

    #: Template referring to the secondary surfactant concentration
    secondary_surfactant_conc = Instance(ParameterTemplate)

    #: Template referring to the salt concentration
    salt_conc = Instance(ParameterTemplate)

    #: List of all template objects required to build Workflow
    parameter_templates = List(Instance(ParameterTemplate))

    #: Determines whether or not to enable secondary surfactant UI
    #: options
    enable_secondary_surfactant = Bool(False)

    # ------------------
    #     Properties
    # ------------------

    #: Factory ID for Workflow
    id = Property(Unicode, depends_on='plugin_id,mco_name')

    # ------------------
    #       View
    # ------------------

    traits_view = View(
        HGroup(
            Group(
                Heading("Primary Surfactant"),
                Item("primary_surfactant_conc",
                     editor=InstanceEditor(),
                     style='custom'
                     ),
                show_labels=False
            ),
            Group(
                Heading("Secondary Surfactant"),
                Item("secondary_surfactant_conc",
                     editor=InstanceEditor(),
                     style='custom',
                     enabled_when='enable_secondary_surfactant'
                     ),
                show_labels=False
            ),
            Group(
                Heading("Salt (NaCl)"),
                Item("salt_conc",
                     editor=InstanceEditor(),
                     style='custom'
                     ),
                show_labels=False
            )
        )
    )

    # ------------------
    #     Defaults
    # ------------------

    def _primary_surfactant_conc_default(self):
        return ParameterTemplate(
                plugin_id=self.id,
                name='primary_surfactant',
                parameter_type='Fixed'
            )

    def _secondary_surfactant_conc_default(self):
        return ParameterTemplate(
                plugin_id=self.id,
                name='secondary_surfactant',
                parameter_type='Fixed'
            )

    def _salt_conc_default(self):
        return ParameterTemplate(
                plugin_id=self.id,
                name='salt',
                parameter_type='Ranged'
            )

    def _parameter_templates_default(self):
        return [self.primary_surfactant_conc, self.salt_conc]

    # ------------------
    #     Listeners
    # ------------------

    def _get_id(self):
        return '.'.join([self.plugin_id, "factory", self.mco_name])

    @on_trait_change('enable_secondary_surfactant')
    def update_secondary_surf_conc(self):

        if not self.enable_secondary_surfactant:
            self.secondary_surfactant_conc = (
                self._secondary_surfactant_conc_default()
            )
            self.parameter_templates = self._parameter_templates_default()
        else:
            if self.secondary_surfactant_conc not in self.parameter_templates:
                self.parameter_templates.insert(
                    1, self.secondary_surfactant_conc
                )

    @on_trait_change('id')
    def update_plugin_id(self):
        self.primary_surfactant_conc.plugin_id = self.id
        self.secondary_surfactant_conc.plugin_id = self.id
        self.salt_conc.plugin_id = self.id

    # ------------------
    #   Public Methods
    # ------------------

    def create_template(self):
        return {
                "id": self.id,
                "model_data": {
                    "parameters": [
                        parameter_template.create_template()
                        for parameter_template in self.parameter_templates
                    ],
                    "kpis": [
                        {"name": "micelle",
                         "objective": "MAXIMISE"},
                        {"name": "cost",
                         "objective": "MINIMISE"}
                    ],
                },
            }
