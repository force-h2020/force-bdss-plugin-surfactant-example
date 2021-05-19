from traits.api import HasTraits, Unicode


class BaseTemplate(HasTraits):
    """Class used to generate template Workflows for a simplified
    ContributedUI"""

    # ---------------------
    #  Required Attributes
    # ---------------------

    #: Surfactant plugin ID for Workflow
    plugin_id = Unicode(allow_none=False)

    def create_template(self):
        return NotImplementedError
