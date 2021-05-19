from traits.api import Property, Unicode

from .base_template import BaseTemplate


class NotificationListenerTemplate(BaseTemplate):

    # ------------------
    #     Properties
    # ------------------

    #: Factory ID for Workflow
    id = Property(Unicode, depends_on='plugin_id')

    #: Gromacs plugin ID for Workflow
    gromacs_plugin_id = Unicode()

    #: Gromacs Factory ID for Workflow
    gromacs_id = Property(Unicode, depends_on='gromacs_plugin_id')

    # ------------------
    #     Listeners
    # ------------------

    def _get_id(self):
        return '.'.join([self.plugin_id, "factory"])

    def _get_gromacs_id(self):
        return '.'.join([self.gromacs_plugin_id, "factory"])

    # ------------------
    #   Public Methods
    # ------------------

    def create_hpc_writer_template(self):
        return {
            "id": f"{self.gromacs_id}.hpc_writer",
            "model_data": {
                "dry_run": False,
            }
        }

    def create_csv_writer_template(self):
        return {
            "id": f"{self.id}.surfactant_csv_writer",
            "model_data": {
                "dry_run": False,
            }
        }

    def create_template(self):
        return [
            self.create_hpc_writer_template(),
            self.create_csv_writer_template()
        ]
